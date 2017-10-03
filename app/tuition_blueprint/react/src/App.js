import React, { Component } from 'react';
import './App.css';

import AppBar from 'material-ui/AppBar';
import Toolbar from 'material-ui/Toolbar';
import Typography from 'material-ui/Typography';
import { withStyles } from 'material-ui/styles';
import Table, { TableBody, TableCell, TableHead, TableRow } from 'material-ui/Table';
import Paper from 'material-ui/Paper';
import IconButton from 'material-ui/IconButton';
import Button from 'material-ui/Button';
import TextField from 'material-ui/TextField';
import Dialog, {
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from 'material-ui/Dialog';

const styles = theme => ({
  paper: {
    width: '100%',
    marginTop: theme.spacing.unit * 3,
    overflowX: 'auto',
  },
});

class Form extends Component {
  constructor(props) {
    super(props);
    this.state = { open: false };
  };
  handleRequestClose = () => {
    this.setState({ open: false });
  };
  handleClickOpen = () => {
    this.setState({ open: true });
  };
  render() {
    return (
      <Dialog open={this.state.open} onRequestClose={this.handleRequestClose}>
        <DialogTitle>{'Subscribe'}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            To subscribe to this website, please enter your email address here. We will send
            updates occationally.
          </DialogContentText>
          <TextField autoFocus margin="dense" id="name" label="Email Address" type="email" fullWidth />
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
    this.state = { customers: [] };
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
  showForm = () => {
    this.form.handleClickOpen();
  };
  render() {
    return (
      <div className="Customers">
        <Form ref={ref => (this.form = ref)} />
        <Paper className={styles.paper}>
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
                  (customer) => {
                    return (
                      <TableRow key={customer.id}>
                        <TableCell >
                          {customer.name}
                        </TableCell>
                        <TableCell>
                          <RecurringPayment recurringPayment={customer.recurring_payment} items={this.items}/>
                        </TableCell>
                        <TableCell style={{textAlign: "center"}}>
                          <IconButton onClick={this.showForm} className="material-icons">{ customer.recurringPayment ? "delete" : "add_circle" }</IconButton>
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

export default withStyles(styles)(App);
