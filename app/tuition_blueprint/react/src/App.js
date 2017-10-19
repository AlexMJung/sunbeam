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
    var n = Number(value.replace(/^\$/, ""));
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
  };
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
  };
  render() {
    const { validationParent, ...props} = this.props;
    this.validationParent = validationParent;
    return (
      <StatefulTextField ref={this.registerComponentForValidation} valid={this.props.validationParent.validateComponent(this).toString()} {...props} />
    )
  };
}

class StatefulTextField extends Component {
  render() {
    return (
      <TextField {...this.props} />
    )
  }
}

class Form extends Component {
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
  };
  componentWillReceiveProps(nextProps) {
    if (nextProps.items && this.state.itemId === "") {
      this.setState({ itemId: nextProps.items[0].id });
      this.setState({ amount: nextProps.items[0].price.toFixed(2) });
    }
  };
  registerComponentForValidation = (component) => {
    // console.log("Register: " + component.props.id);
    this.componentsToValidate.push(component)
  }
  validate = () => {
    for (var i = 0; i < this.componentsToValidate.length; i++) {
      if (this.componentsToValidate[i].props.valid === "false") {
        console.log("First invalid: " + this.componentsToValidate[i].props.id);
        this.setState({ valid: false });
        return
      }
    }
    this.setState({ valid: true });
  };
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
  };
  requestClose = () => {
    this.setState(this.baseState)
  };
  open = () => {
    this.setState({ open: true });
  };
  item = e => {
    this.setState({ itemId: e.target.value });
    this.setState({ amount: this.props.items.find((item) => { return (item.id === e.target.value); }).price });

  }
  change = e => {
    this.setState({[e.target.name]: e.target.value});
  };
  submit = () => {
  };
  render() {
    if (this.props.customer && this.props.items) {
      return (
        <Dialog open={this.state.open} onRequestClose={this.requestClose}>
          <DialogTitle>{'Recurring Payment'}</DialogTitle>
          <DialogContent>
            <DialogContentText>
              All of the fields on this form are required:
            </DialogContentText>
            <TextField margin="dense" disabled={true} id="name" label="Name" value={this.props.customer.name} fullWidth />
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
            <NumberFormat validationParent={this} validators={[Validators.required, Validators.positiveAmount]} margin="dense" id="amount" decimalPrecision={2} label="Amount" customInput={ValidatedTextField} value={this.state.amount} thousandSeparator={true} prefix={'$'} onChange={this.change} name="amount" fullWidth/>
            <NumberFormat validationParent={this} validators={[Validators.required, Validators.monthNumber]} margin="dense" id="endDateMonth" name="endDateMonth" label="Last Payment Month" customInput={ValidatedTextField} value={this.state.endDateMonth} onChange={this.change} style={ {width: "48%", marginRight: "4%"} } format="##" />
            <NumberFormat validationParent={this} validators={[Validators.required, Validators.yearNumber]} margin="dense" id="endDateYear" name="endDateYear" label="Last Payment Year" customInput={ValidatedTextField} value={this.state.endDateYear} onChange={this.change} format="##" style={ {width: "48%"} }/>
            <FormControl margin="dense" fullWidth>
              <InputLabel shrink={true} htmlFor="amount">Payment Method</InputLabel><br/>
              <RadioGroup name="paymentMethod" value={this.state.paymentMethod} onChange={this.change}  style={{ display: 'inline' }}>
                <FormControlLabel value="credit-card" control={<Radio />} label="Credit card" />
                <FormControlLabel value="e-check" control={<Radio />} label="E-check" />
              </RadioGroup>
            </FormControl>
            { this.state.paymentMethod === "credit-card" &&
              <div>
                <NumberFormat validationParent={this} validators={[Validators.required, Validators.creditCardNumber]} margin="dense" fullWidth label="Credit Card Number" id="creditCardNumber" name="creditCardNumber" customInput={ValidatedTextField} value={this.state.creditCardNumber} onChange={this.change} format="#### #### #### ####" />
                <NumberFormat validationParent={this} validators={[Validators.required, Validators.monthNumber]} margin="dense" label="Expiration Month" id="creditCardExpirationMonth" name="creditCardExpirationMonth" customInput={ValidatedTextField} value={this.state.creditCardExpirationMonth} onChange={this.change} format="##" style={ {width: "32%", marginRight: "2%" } }/>
                <NumberFormat validationParent={this} validators={[Validators.required, Validators.yearNumber]} label="Expiration Year" id="creditCardExpirationYear" name="creditCardExpirationYear" customInput={ValidatedTextField} value={this.state.creditCardExpirationYear} onChange={this.change} format="##" style={ {width: "32%", marginRight: "2%" } }/>
                <NumberFormat validationParent={this} validators={[Validators.required, Validators.creditCardSecurityCode]} label="Security Code" id="creditCardSecurityCode" name="creditCardSecurityCode" customInput={ValidatedTextField} value={this.state.creditCardSecurityCode} onChange={this.change} format="###" style={ {width: "32%" } }/>
              </div>
            }
            { this.state.paymentMethod === "e-check" &&
              <div>
                <ValidatedTextField validationParent={this} validators={[Validators.required]} id="checkingName" name="checkingName" label="Name on Checking Account"  value={this.state.checkingName} onChange={this.change} style={ {width: "48%", marginRight: "4%" } } />
                <NumberFormat validationParent={this} validators={[Validators.required]} id="checkingPhone" name="checkingPhone" label="Phone Number" customInput={ValidatedTextField} value={this.state.checkingPhone} onChange={this.change} format="### ### ####" style={ {width: "48%" } } />
                <NumberFormat validationParent={this} validators={[Validators.required]} id="checkingRoutingNumber" name="checkingRoutingNumber" label="Routing Number" customInput={ValidatedTextField} value={this.state.checkingRoutingNumber} onChange={this.change} format="#########" style={ {width: "48%", marginRight: "4%" } }/>
                <NumberFormat validationParent={this} validators={[Validators.required]} id="checkingAccountNumber" name="checkingAccountNumber" label="Checking Account Number" customInput={ValidatedTextField} value={this.state.checkingAccountNumber} onChange={this.change} style={ {width: "48%"} }/>
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

class RecurringPayment extends Component {
  render() {
    if (this.props.recurringPayment) {
      // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/filter
      return "TBD"
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
      selectedCustomer: null
     };
    fetch("http://localhost:5000/tuition/customers", {credentials: 'include'})
      .then( (response) => {
        return response.json()
      }).then( (parsed_json) => {
        this.setState({customers: parsed_json})
      });
    fetch("http://localhost:5000/tuition/items", {credentials: 'include'})
      .then( (response) => {
        return response.json()
      }).then( (parsed_json) => {
        this.setState({items: parsed_json})
      });
  };
  showForm = (index) => {
    this.setState({selectedCustomer: this.state.customers[index]});
    this.form.open();
  };
  render() {
    return (
      <div className="Customers">
        <Form ref={form => (this.form = form)} items={this.state.items} customer={this.state.selectedCustomer}/>
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
                          <RecurringPayment recurringPayment={customer.recurring_payment} items={this.items}/>
                        </TableCell>
                        <TableCell style={{textAlign: "center"}}>
                          <IconButton onClick={ () => this.showForm(index) } className="material-icons">{ customer.recurringPayment ? "delete" : "add_circle" }</IconButton>
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

class App extends Component {
  render() {
    return (
      <div className="App">
        <AppBar position="static" color="default">
          <Toolbar>
            <Typography type="title" color="inherit">
              Wildflower Tuition Utility
            </Typography>
          </Toolbar>
        </AppBar>
        <Customers/>
      </div>
    );
  }
}

export default App;
