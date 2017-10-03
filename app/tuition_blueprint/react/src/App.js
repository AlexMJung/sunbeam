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
import { FormControl } from 'material-ui/Form';

class Form extends Component {
  constructor(props) {
    super(props);
    this.state = {
      open: false,
      customers: props.customers
    };
  };
  handleRequestClose = () => {
    this.setState({ open: false });
  };
  handleClickOpen = () => {
    this.setState({ open: true });
  };
  selectItem = () => {

  }
  render() {
    if (this.props.customer && this.props.items) {
      return (
        <Dialog open={this.state.open} onRequestClose={this.handleRequestClose}>
          <DialogTitle>{'Recurring Payment'}</DialogTitle>
          <DialogContent>
            <DialogContentText>
              { /* instructions here */ }
            </DialogContentText>
            <TextField autoFocus margin="dense" disabled={true} id="name" label="Name"value={this.props.customer.name} fullWidth/>
            <FormControl>
              <InputLabel autoWidth htmlFor="age-simple">Item</InputLabel>
              <Select autoWidth onChange={this.selectItem} value={"0"} input={<Input id="item-id" />}>
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
          </DialogContent>
          <DialogActions>
            <Button onClick={this.handleRequestClose} color="primary">
              Cancel
            </Button>
            <Button onClick={this.handleRequestClose} color="primary">
              Subscribe
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
