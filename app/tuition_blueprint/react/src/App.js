import React, { Component } from 'react';
import './App.css';
import AppBar from 'material-ui/AppBar';
import Toolbar from 'material-ui/Toolbar';
import Typography from 'material-ui/Typography';
import Table, { TableBody, TableCell, TableHead, TableRow } from 'material-ui/Table';
import Paper from 'material-ui/Paper';
import IconButton from 'material-ui/IconButton';
import Button from 'material-ui/Button';
import TextField from 'material-ui/TextField';
import Dialog, { DialogActions, DialogContent, DialogContentText, DialogTitle} from 'material-ui/Dialog';
import { MenuItem } from 'material-ui/Menu';
import Select from 'material-ui/Select';
import Input, { InputLabel } from 'material-ui/Input';
import { FormControl, FormControlLabel } from 'material-ui/Form';
import NumberFormat from 'react-number-format';
import Radio, { RadioGroup } from 'material-ui/Radio';
import { MuiThemeProvider, createMuiTheme } from 'material-ui/styles';
import Snackbar from 'material-ui/Snackbar';
import CloseIcon from 'material-ui-icons/Close';


var tuitionBlueprintBaseUrl = "http://localhost:5000/tuition";
var qboBaseUrl = "https://sandbox.api.intuit.com"

// https://gist.github.com/ShirtlessKirk/2134376
var luhnChk = (function (arr) {
    return function (ccNum) {
        var
            len = ccNum.length,
            bit = 1,
            sum = 0,
            val;

        while (len) {
            val = parseInt(ccNum.charAt(--len), 10);
            sum += (bit ^= 1) ? arr[val] : val; // eslint-disable-line no-cond-assign
        }

        return sum && sum % 10 === 0;
    };
}([0, 2, 4, 6, 8, 1, 3, 5, 7, 9]));

class Validators {
  static required = value => {
    if (value) {
      return true;
    }
    return false;
  }

  static positiveAmount = value => {
    var n = Number(value.replace(/^\$|,/g, ""));
    if (n > 0) {
      return true;
    }
    return false;
  }

  static monthNumber = value => {
    var n = Number(value);
    if (12 >= n >= 1) {
      return true;
    }
    return false;
  }

  static yearNumber = value => {
    var n = Number(value)
    if (n >= new Date().getFullYear() - 2000) {
      return true;
    }
    return false;
  }

  static creditCardNumber = value => {
    if (value.length === 19 && luhnChk(value.replace(/ /g,""))) {
      return true;
    }
    return false;
  }

  static creditCardSecurityCode = value => {
    if (value.length === 3) {
      return true;
    }
    return false;
  }

  static minimumLength = l => {
    return value => {
      if (value.length >= l ) {
        return true;
      }
      return false;
    }
  }
}

class ValidatedTextField extends Component {
  constructor(props) {
    super(props);
    this.lastValue = null;
  }

  registerComponentForValidation = ref => {
    if (ref) { // ignore when called with null; see https://github.com/facebook/react/issues/9328
      this.validationParent.registerComponentForValidation(ref)
    }
  }

  componentDidUpdate() {
    // this creates a state change, which causes componentDidUpdate to be called again
    // so, only validate if the value changed
    if (this.props.value !== this.lastValue) {
      this.lastValue = this.props.value;
      this.validationParent.validateComponent(this);
      this.validationParent.validate();
    }
  }

  componentWillUnmount() {
    this.validationParent.unRegisterComponentForValidation(this)
  }

  render() {
    const { validationParent, ...props} = this.props;
    this.validationParent = validationParent;
    var valid = this.props.validationParent.validateComponent(this)
    return (
      <StatefulTextField ref={this.registerComponentForValidation} valid={valid.toString()} error={ this.props.value !== "" && ! valid } {...props} />
    )
  }
}

class StatefulTextField extends Component {
  render() {
    return (
      <TextField {...this.props} />
    )
  }
}

class AddForm extends Component {
  constructor(props) {
    super(props);
    this.componentsToValidate = [];
    this.state = {
      open: false,
      itemId: "",
      amount: "",
      paymentMethod: "credit-card",
      endDateMonth: "",
      endDateYear: "",
      creditCardNumber: "",
      creditCardExpirationMonth: "",
      creditCardExpirationYear: "",
      creditCardSecurityCode: "",
      checkingName: "",
      checkingAccountNumber: "",
      checkingRoutingNumber: "",
      checkingPhone: "",
      valid: false
    };
    this.baseState = this.state
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.items && this.state.itemId === "") {
      this.baseState.itemId = nextProps.items[0].id
      this.baseState.amount = nextProps.items[0].price.toFixed(2)
      this.setState({
        itemId: nextProps.items[0].id,
        amount: nextProps.items[0].price.toFixed(2)
      });
    }
  }

  registerComponentForValidation = (component) => {
    // console.log("Register: " + component.props.id);
    this.componentsToValidate.push(component)
  }

  validate = () => {
    for (var i = 0; i < this.componentsToValidate.length; i++) {
      if (this.componentsToValidate[i].props.valid === "false") {
        // console.log("First invalid: " + this.componentsToValidate[i].props.id);
        this.setState({ valid: false });
        return
      }
    }
    this.setState({ valid: true });
  }

  validateComponent = component => {
    var validators = component.props.validators
    if (! Array.isArray(validators)) {
      validators = [validators];
    }
    for (var i = 0; i < validators.length; i++) {
      var validator = validators[i]
      if (! validator(component.props.value)) {
        return false;
      }
    }
    return true;
  }

  unRegisterComponentForValidation = component => {
    for (var i = 0; i < this.componentsToValidate.length; i++) {
      if (this.componentsToValidate[i].props.id === component.props.id) {
          // console.log("Unregister: " + component.props.id)
          this.componentsToValidate.splice(i, 1);
          return;
      }
    }
  }

  requestClose = () => this.setState({ open: false});

  open = () => {
    this.setState(this.baseState);
    this.setState({ open: true });
  }

  item = e => {
    this.setState({
      itemId: e.target.value,
      amount: this.props.items.find((item) => { return (item.id === e.target.value); }).price.toString()
    });
  }

  change = e => this.setState({[e.target.name]: e.target.value});

  submit = async () => {
    this.requestClose();
    if (this.state.paymentMethod === 'credit-card') {
      var tokenUrl = qboBaseUrl + "/quickbooks/v4/payments/tokens";
      var tokenParams = {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        method: "POST",
        body: JSON.stringify(
          {
            "card": {
              expYear: "20" + this.state.creditCardExpirationYear,
              expMonth: this.state.creditCardExpirationMonth.padStart(2, "0"),
              number: this.state.creditCardNumber.replace(/\s+/g, ''),
              cvc: this.state.creditCardSecurityCode
            }
          }
        ),
        credentials: 'omit'
      };
      var token = await fetch(tokenUrl,tokenParams)
        .then(response => this.props.handleAPIErrors({url: tokenUrl, params: tokenParams, response: response}))
        .then(response => response.json())
        .then(parsed_json => parsed_json['value'])
        .catch(error => this.props.handleAPIErrors({url: tokenUrl, params: tokenParams, error: error}));
      if (token) {
        var creditCardUrl = tuitionBlueprintBaseUrl + "/credit_card";
        var creditCardParams = {
          credentials: 'include',
          method: "POST",
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            customer_id: this.props.customer.id,
            token: token
          })
        };
        var creditCardId = await fetch(creditCardUrl, creditCardParams)
          .then(response => this.props.handleAPIErrors({url: creditCardUrl, params: creditCardParams, response: response}))
          .then(response => response.json())
          .then(parsed_json => parsed_json["id"])
          .catch(error => this.props.handleAPIErrors({url: creditCardUrl, params: creditCardParams, error: error}));
      }
    } else if (this.state.paymentMethod === 'e-check') {
      var bankAccountUrl = tuitionBlueprintBaseUrl + "/bank_account";
      var bankAccountParams = {
        credentials: 'include',
        method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customer_id: this.props.customer.id,
          name: this.state.checkingName,
          routing_number: this.state.checkingRoutingNumber,
          account_number: this.state.checkingAccountNumber,
          phone: this.state.checkingPhone.replace(/\s+/g, '')
        })
      };
      var bankAccountId = await fetch(bankAccountUrl, bankAccountParams)
        .then(response => this.props.handleAPIErrors({url: bankAccountUrl, params: creditCardParams, response: response}))
        .then(response => response.json())
        .then(parsed_json => parsed_json["id"])
        .catch(error => this.props.handleAPIErrors({url: bankAccountUrl, params: bankAccountParams, error: error}));
    }

    if (creditCardId || bankAccountId) {
      var startDate = new Date();
      startDate.setDate(1);
      startDate.setMonth(startDate.getMonth() + 1);
      startDate.setUTCHours(0,0,0,0);

      var endDate = new Date();
      endDate.setMonth(this.state.endDateMonth - 1);
      endDate.setDate(28);
      endDate.setFullYear("20" + this.state.endDateYear);
      endDate.setUTCHours(0,0,0,0);

      var recurringPaymentsUrl = tuitionBlueprintBaseUrl + "/recurring_payments";
      var recurringPaymentsParams = {
        credentials: 'include',
        method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customer_id: this.props.customer.id,
          bank_account_id: bankAccountId,
          credit_card_id: creditCardId,
          item_id: this.state.itemId,
          amount: this.state.amount.replace(/^\$/g,''),
          start_date: startDate,
          end_date: endDate,
        })
      }
      var recurringPayment = fetch(recurringPaymentsUrl, recurringPaymentsParams)
        .then(response => this.props.handleAPIErrors({url: recurringPaymentsUrl, params: recurringPaymentsParams, response: response}))
        .then(response => response.json())
        .catch(error => this.props.handleAPIErrors({url: recurringPaymentsUrl, params: recurringPaymentsParams, error: error}));
    }
    this.props.addRecurringPaymentForSelectedCustomerFunction(recurringPayment);
  }

  render() {
    if (this.props.customer && this.props.items) {
      return (
        <Dialog open={this.state.open} onRequestClose={this.requestClose}>
          <DialogTitle>{'Recurring Payment'}</DialogTitle>
          <DialogContent>
            <DialogContentText>
              All of the fields on this form are required:
            </DialogContentText>
            <TextField margin="dense" disabled id="name" label="Name" value={this.props.customer.name} fullWidth />
            <FormControl margin="dense" fullWidth>
              <InputLabel htmlFor="item-id">Item</InputLabel>
              <Select onChange={this.item} value={this.state.itemId} input={<Input id="item-id" fullWidth />}>
                {
                  this.props.items.map(
                    (item, index) => {
                      return (
                        <MenuItem key={index} value={item.id}>{item.name}</MenuItem>
                      )
                    }
                  )
                }
              </Select>
            </FormControl>
            <NumberFormat validationParent={this} validators={[Validators.required, Validators.positiveAmount]} margin="dense" id="amount" decimalPrecision={2} label="Amount" customInput={ValidatedTextField} value={this.state.amount} thousandSeparator prefix={'$'} onChange={this.change} name="amount" fullWidth />
            <Typography type="caption" style={{marginTop: "20px"}}>
              Payment will begin on the first of next month.
            </Typography>
            <NumberFormat validationParent={this} validators={[Validators.required, Validators.monthNumber]} margin="dense" id="endDateMonth" name="endDateMonth" label="Last Payment Month" customInput={ValidatedTextField} value={this.state.endDateMonth} onChange={this.change} style={{width: "48%", marginRight: "4%"}} format="##" />
            <NumberFormat validationParent={this} validators={[Validators.required, Validators.yearNumber]} margin="dense" id="endDateYear" name="endDateYear" label="Last Payment Year" customInput={ValidatedTextField} value={this.state.endDateYear} onChange={this.change} format="##" style={{width: "48%"}} />
            <FormControl margin="dense" fullWidth>
              <InputLabel shrink htmlFor="amount">Payment Method</InputLabel><br />
              <RadioGroup name="paymentMethod" value={this.state.paymentMethod} onChange={this.change}  style={{ display: 'inline' }}>
                <FormControlLabel value="credit-card" control={<Radio />} label="Credit card" />
                <FormControlLabel value="e-check" control={<Radio />} label="E-check" />
              </RadioGroup>
            </FormControl>
            { this.state.paymentMethod === "credit-card" &&
              <div>
                <NumberFormat validationParent={this} validators={[Validators.required, Validators.creditCardNumber]} margin="dense" fullWidth label="Credit Card Number" id="creditCardNumber" name="creditCardNumber" customInput={ValidatedTextField} value={this.state.creditCardNumber} onChange={this.change} format="#### #### #### ####" />
                <NumberFormat validationParent={this} validators={[Validators.required, Validators.monthNumber]} margin="dense" label="Expiration Month" id="creditCardExpirationMonth" name="creditCardExpirationMonth" customInput={ValidatedTextField} value={this.state.creditCardExpirationMonth} onChange={this.change} format="##" style={{width: "32%", marginRight: "2%" }} />
                <NumberFormat validationParent={this} validators={[Validators.required, Validators.yearNumber]} label="Expiration Year" id="creditCardExpirationYear" name="creditCardExpirationYear" customInput={ValidatedTextField} value={this.state.creditCardExpirationYear} onChange={this.change} format="##" style={{width: "32%", marginRight: "2%" }} />
                <NumberFormat validationParent={this} validators={[Validators.required, Validators.creditCardSecurityCode]} label="Security Code" id="creditCardSecurityCode" name="creditCardSecurityCode" customInput={ValidatedTextField} value={this.state.creditCardSecurityCode} onChange={this.change} format="###" style={{width: "32%" }} />
              </div>
            }
            { this.state.paymentMethod === "e-check" &&
              <div>
                <ValidatedTextField validationParent={this} validators={[Validators.required, Validators.minimumLength(3)]} id="checkingName" name="checkingName" label="Name on Checking Account"  value={this.state.checkingName} onChange={this.change} style={{width: "48%", marginRight: "4%" }} />
                <NumberFormat validationParent={this} validators={[Validators.required, Validators.minimumLength(10)]} id="checkingPhone" name="checkingPhone" label="Phone Number" customInput={ValidatedTextField} value={this.state.checkingPhone} onChange={this.change} format="### ### ####" style={{width: "48%" }} />
                <NumberFormat validationParent={this} validators={[Validators.required, Validators.minimumLength(9)]} id="checkingRoutingNumber" name="checkingRoutingNumber" label="Routing Number" customInput={ValidatedTextField} value={this.state.checkingRoutingNumber} onChange={this.change} format="#########" style={{width: "48%", marginRight: "4%" }} />
                <NumberFormat validationParent={this} validators={[Validators.required, Validators.minimumLength(5)]} id="checkingAccountNumber" name="checkingAccountNumber" label="Checking Account Number" customInput={ValidatedTextField} value={this.state.checkingAccountNumber} onChange={this.change} style={{width: "48%"}} />
              </div>
            }
          </DialogContent>
          <DialogActions>
            <Button onClick={this.requestClose} color="primary">
              Cancel
            </Button>
            <Button disabled={!this.state.valid} onClick={this.submit} color="primary" >
              Save
            </Button>
          </DialogActions>
        </Dialog>
      );
    }
    return (null);
  }
}

class DeleteForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      open: false,
    };
  }

  requestClose = () => this.setState({open: false});

  open = () => this.setState({ open: true });

  delete = () => {
    this.requestClose();
    var deleteRecurringPaymentUrl = tuitionBlueprintBaseUrl + "/recurring_payments/" + this.props.customer.recurring_payment.id;
    var deleteRecurringPaymentParams = {
      credentials: 'include',
      method: "DELETE",
    }
    fetch(deleteRecurringPaymentUrl, deleteRecurringPaymentParams)
      .then(response => this.props.handleAPIErrors({url: deleteRecurringPaymentUrl, params: deleteRecurringPaymentParams, response: response}))
      .catch(error => this.props.handleAPIErrors({url: deleteRecurringPaymentUrl, params: deleteRecurringPaymentParams, error: error}));
    this.props.deleteRecurringPaymentForSelectedCustomerFunction();
  }

  render() {
    if (this.props.customer) {
      return (
        <div>
          <Dialog open={this.state.open} onRequestClose={this.requestClose}>
            <DialogTitle>Confirm Deletion </DialogTitle>
            <DialogContent>
              <DialogContentText>
                Please confirm that you want to delete the recurring tuition payment for { this.props.customer.name }.
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <Button onClick={this.requestClose} color="primary">
                Cancel
              </Button>
              <Button onClick={this.delete} color="primary" >
                Delete
              </Button>
          </DialogActions>
          </Dialog>
        </div>
      )
    }
    return (null);
  }
}

class APIErrorSnackbar extends Component {
  state = {
    open: false,
  };

  open = () => this.setState({open: true});

  handleRequestClose = () => this.setState({open: false});

  render() {
    return (
      <Snackbar
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left',}}
        open={this.state.open}
        onRequestClose={this.requestClose}
        message={<span id="message-id">API Error: {this.props.error} <a href={"mailto:support@wildflowerschools.org?subject=Tuition utility API error&body=%0A%0AAPI Details: " + this.props.error} style={{color: "white"}}>submit support request</a></span>}
        action={[<IconButton key="close" color="inherit" onClick={this.handleRequestClose}><CloseIcon /></IconButton>]}
      />
    )
  }
}

class RecurringPayment extends Component {
  render() {
    if (this.props.recurringPayment) {
      var item = this.props.items.filter(item => item.id === this.props.recurringPayment.item_id)[0]
      var endDate = new Date(this.props.recurringPayment.end_date);
      return item.name + ", $" + (this.props.recurringPayment.amount).toLocaleString() + "/month, through " + endDate.toLocaleString("en-us", { month: "long" }) + " of " + endDate.getFullYear();
    } else {
      return "None"
    }
  }
}

class Customers extends Component {
  constructor(props) {
    super(props);
    this.state = {
      customers: [],
      selectedCustomer: null,
      apiError: ""
     };

     var itemsUrl = tuitionBlueprintBaseUrl + "/items";
     var itemsParams = {credentials: 'include'};
     fetch(itemsUrl, itemsParams)
       .then(response => this.handleAPIErrors({url: itemsUrl, params: itemsParams, response: response}))
       .then(response => response.json())
       .then(parsed_json => this.setState({items: parsed_json}))
       .catch(error => this.handleAPIErrors({url: itemsUrl, params: itemsParams, error: error}));

    var customersUrl = tuitionBlueprintBaseUrl + "/customers";
    var customersParams = {credentials: 'include'};
    fetch(customersUrl, customersParams)
      .then(response => this.handleAPIErrors({url: customersUrl, params: customersParams, response: response}))
      .then(response => response.json())
      .then(parsed_json => this.setState({customers: parsed_json}))
      .catch(error => this.handleAPIErrors({url: customersUrl, params: customersParams, error: error}));
  }
  handleAPIErrors = ({url, params, response, error}={}) => {
    if (error) {
      if (error.message !== "handleAPIErrors") {
        this.setState({apiError: error.message + " (" + url + " " + JSON.stringify(params) + ")" });
        this.apiErrorSnackbar.open();
      }
    } else if (response.status >= 200 && response.status < 300) {
      return response
    } else if (response.status === 401) {
      window.location.href = tuitionBlueprintBaseUrl;
    } else {
      response.text().then(text  => {
        this.setState({apiError: " Unexpected results (" + url + " " + JSON.stringify(params) + " " + text + ")" });
        this.apiErrorSnackbar.open();
      });
      throw Error("handleAPIErrors");
    }
  }

  showAddForm = index => {
    this.setState({selectedCustomer: this.state.customers[index]});
    this.addForm.open();
  }

  addRecurringPaymentForSelectedCustomer = recurring_payment => {
    recurring_payment.then((recurring_payment) => {
      var customers = this.state.customers;
      var index = customers.findIndex(customer => customer.id === this.state.selectedCustomer.id);
      customers[index].recurring_payment = recurring_payment;
      this.setState({customers: customers});
    });
  }

  showDeleteForm = index => {
    this.setState({selectedCustomer: this.state.customers[index]});
    this.deleteForm.open();
  }

  deleteRecurringPaymentForSelectedCustomer = () => {
    var customers = this.state.customers;
    var index = customers.findIndex(customer => customer.id === this.state.selectedCustomer.id);
    customers[index].recurring_payment = null;
    this.setState({customers: customers});
  }

  render() {
    return (
      <div className="Customers">
        <APIErrorSnackbar ref={apiErrorSnackbar => (this.apiErrorSnackbar = apiErrorSnackbar)} error={this.state.apiError} />
        <AddForm ref={addForm => (this.addForm = addForm)} items={this.state.items} customer={this.state.selectedCustomer} handleAPIErrors={this.handleAPIErrors} addRecurringPaymentForSelectedCustomerFunction={this.addRecurringPaymentForSelectedCustomer} />
        <DeleteForm ref={deleteForm => (this.deleteForm = deleteForm)} customer={this.state.selectedCustomer} handleAPIErrors={this.handleAPIErrors} deleteRecurringPaymentForSelectedCustomerFunction={this.deleteRecurringPaymentForSelectedCustomer} />
        <Paper>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Customer</TableCell>
                <TableCell>Recurring Payment</TableCell>
                <TableCell style={{width: 56, textAlign: "center"}}>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {
                this.state.customers.map(
                  (customer, index) => {
                    return (
                      <TableRow key={customer.id}>
                        <TableCell >
                          {customer.name}
                        </TableCell>
                        <TableCell>
                          <RecurringPayment recurringPayment={customer.recurring_payment} items={this.state.items} />
                        </TableCell>
                        <TableCell style={{textAlign: "center"}}>
                          { customer.recurring_payment &&
                            <IconButton color="accent" onClick={ () => this.showDeleteForm(index) } className="material-icons">remove_circle_outline</IconButton>
                          }
                          { ! customer.recurring_payment &&
                            <IconButton color="accent" onClick={ () => this.showAddForm(index) } className="material-icons">add_circle_outline</IconButton>
                          }
                        </TableCell>
                      </TableRow>
                    )
                  }
                )
              }
            </TableBody>
          </Table>
        </Paper>
      </div>
    );
  }
}

const theme = createMuiTheme({
  palette: {
    primary: {
      '50': '#e0f4f3',
      '100': '#b3e4e1',
      '200': '#80d3ce',
      '300': '#4dc1ba',
      '400': '#26b3ab',
      '500': '#00a69c',
      '600': '#009e94',
      '700': '#00958a',
      '800': '#008b80',
      '900': '#007b6e',
      'A100': '#b3e4e1',
      'A200': '#80d3ce',
      'A400': '#26b3ab',
      'A700': '#00958a',
      contrastDefaultColor: 'light'
    },
    secondary: {
      '50': '#e3eeee',
      '100': '#b8d4d4',
      '200': '#89b8b8',
      '300': '#5a9b9b',
      '400': '#368585',
      '500': '#137070',
      '600': '#116868',
      '700': '#0e5d5d',
      '800': '#0b5353',
      '900': '#064141',
      'A100': '#B8D4D4',
      'A200': '#89B8B8',
      'A400': '#368585',
      'A700': '#0E5D5D',
      contrastDefaultColor: 'light'
    },
    error: {
      '50': '#fdede5',
      '100': '#fbd3bd',
      '200': '#f9b691',
      '300': '#f69865',
      '400': '#f48244',
      '500': '#f26c23',
      '600': '#f0641f',
      '700': '#ee591a',
      '800': '#ec4f15',
      '900': '#e83d0c',
      'A100': '#FBD3BD',
      'A200': '#F9B691',
      'A400': '#F48244',
      'A700': '#EE591A',
      contrastDefaultColor: 'light'
    }
  },
});

class App extends Component {
  render() {
    return (
      <MuiThemeProvider theme={theme}>
        <div className="App">
          <AppBar position="static">
            <Toolbar>
              <Typography type="title" color="inherit">
                Wildflower Tuition Utility
              </Typography>
              <img src="logo.png" alt="logo" style={{marginLeft: "auto", height: "40px"}} />
            </Toolbar>
          </AppBar>
          <Customers />
        </div>
      </MuiThemeProvider>

    );
  }
}

export default App;
