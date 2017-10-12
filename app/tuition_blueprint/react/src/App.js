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

class Form extends Component {
  constructor(props) {
    super(props);
    this.state = {
      open: false,
      itemId: "",
      amount: "",
      paymentMethod: "",
      creditCardNumber: "",
      creditCardExpirationMonth: "",
      creditCardExpirationYear: "",
      creditCardSecurityCode: "",
      checkingName: "",
      checkingAccountNumber: "",
      checkingRoutingNumber: "",
      checkingPhone: ""
    };
    this.baseState = this.state
  };
  componentWillReceiveProps(nextProps) {
    if (nextProps.items && this.state.itemId === "") {
      this.setState({ itemId: nextProps.items[0].id });
      this.setState({ amount: nextProps.items[0].price.toFixed(2) });
    }
  }
  handleRequestClose = () => {
    this.setState(this.baseState)
  };
  handleClickOpen = () => {
    this.setState({ open: true });
  };
  selectItem = event => {
    this.setState({ itemId: event.target.value });
    this.setState({ amount: this.props.items.find((item) => { return (item.id === event.target.value); }).price });
  }

  onChange = e => {
    this.setState({[e.target.name]: e.target.value});
  }

// XXX handle blur/focus

// XXX update CC fields to use blur/focus for shrink

  render() {
    if (this.props.customer && this.props.items) {
      return (
        <Dialog open={this.state.open} onRequestClose={this.handleRequestClose}>
          <DialogTitle>{'Recurring Payment'}</DialogTitle>
          <DialogContent>
            <DialogContentText>
              { /* instructions here */ }
            </DialogContentText>
            <TextField margin="dense" disabled={true} id="name" label="Name" value={this.props.customer.name} fullWidth />
            <FormControl margin="dense" fullWidth>
              <InputLabel htmlFor="item-id">Item</InputLabel>
              <Select onChange={this.selectItem} value={this.state.itemId} input={<Input id="item-id" fullWidth />}>
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
            <FormControl margin="dense" fullWidth>
              <InputLabel shrink={true} htmlFor="amount">Amount</InputLabel><br/>
              <NumberFormat id="amount" decimalPrecision={2} customInput={TextField} value={this.state.amount} thousandSeparator={true} prefix={'$'} onChange={this.onChange} name="amount" fullWidth />
            </FormControl>
            <FormControl margin="dense" fullWidth>
              <InputLabel shrink={true} htmlFor="amount">Payment Method</InputLabel><br/>
              <RadioGroup name="paymentMethod" value={this.state.paymentMethod} onChange={this.onChange}  style={{ display: 'inline' }}>
                <FormControlLabel value="credit-card" control={<Radio />} label="Credit card" />
                <FormControlLabel value="e-check" control={<Radio />} label="E-check" />
              </RadioGroup>
            </FormControl>
            { this.state.paymentMethod === "credit-card" &&
              <div>
                <FormControl margin="dense" fullWidth>
                  <InputLabel shrink={true} htmlFor="creditCardNumber">Credit Card Number</InputLabel><br/>
                  <NumberFormat id="creditCardNumber" name="creditCardNumber" customInput={TextField} value={this.state.creditCardNumber} onChange={this.onChange} format="#### #### #### ####" fullWidth />
                </FormControl>
                <FormControl margin="dense" >
                  <InputLabel shrink={true} htmlFor="creditCardExpirationMonth">Expiration Month</InputLabel><br/>
                  <NumberFormat id="creditCardExpirationMonth" name="creditCardExpirationMonth" customInput={TextField} value={this.state.creditCardExpirationMonth} onChange={this.onChange} format="##" />
                </FormControl>
                &nbsp;
                <FormControl margin="dense" >
                  <InputLabel shrink={true} htmlFor="amount">Expiration Year</InputLabel><br/>
                  <NumberFormat id="creditCardExpirationYear" name="creditCardExpirationYear" customInput={TextField} value={this.state.creditCardExpirationYear} onChange={this.onChange} format="##" />
                </FormControl>
                &nbsp;
                <FormControl margin="dense" >
                  <InputLabel shrink={true} htmlFor="creditCardSecurityCode">Security Code</InputLabel><br/>
                  <NumberFormat id="creditCardSecurityCode" name="creditCardSecurityCode" customInput={TextField} value={this.state.creditCardSecurityCode} onChange={this.onChange} format="###" />
                </FormControl>
              </div>
            }
            { this.state.paymentMethod === "e-check" &&
              <div>
                <TextField margin="dense" id="checkingName" name="checkingName" label="Name on Checking Account" value={this.state.checkingName} onChange={this.onChange} fullWidth />
                <FormControl margin="dense" style={ {width: "48%", marginRight: "4%" } }>
                  <InputLabel shrink={ this.state.checkingAccountNumber !== "" } htmlFor="checkingAccountNumber">Checking Account Number</InputLabel><br/>
                  <NumberFormat id="checkingAccountNumber" name="checkingAccountNumber" customInput={TextField} value={this.state.checkingAccountNumber} onChange={this.onChange} />
                </FormControl>
                <FormControl margin="dense" style={ {width: "48%"} }>
                  <InputLabel shrink={ this.state.checkingRoutingNumber !== "" } htmlFor="checkingRoutingNumber">Routing Number</InputLabel><br/>
                  <NumberFormat id="checkingRoutingNumber" name="checkingRoutingNumber" customInput={TextField} value={this.state.checkingRoutingNumber} onChange={this.onChange} format="#########" fullWidth />
                </FormControl>
              </div>
            }
          </DialogContent>
          <DialogActions>
            <Button onClick={this.handleRequestClose} color="primary">
              Discard
            </Button>
            <Button onClick={this.handleRequestClose} color="primary">
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
    this.form.handleClickOpen();
  };
  render() {
    return (
      <div className="Customers">
        <Form ref={ref => (this.form = ref)} items={this.state.items} customer={this.state.selectedCustomer}/>
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
              Tuition Utility
            </Typography>
          </Toolbar>
        </AppBar>
        <Customers />
      </div>
    );
  }
}

export default App;
