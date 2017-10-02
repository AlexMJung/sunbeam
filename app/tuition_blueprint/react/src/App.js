import React, { Component } from 'react';
import './App.css';

class App extends Component {
  constructor(props) {
    super(props);
    var that = this;
    fetch("http://localhost:5000/tuition/customers", {credentials: 'include'})
      .then(function(response) {
        that.customers = response.json()
      })
    fetch("http://localhost:5000/tuition/items", {credentials: 'include'})
      .then(function(response) {
        that.items = response.json()
      })
    fetch("http://localhost:5000/tuition/recurring_payments", {credentials: 'include'})
      .then(function(response) {
        that.recurring_payments = response.json()
      })
  }
  render() {
    return (
      <div className="App">

      </div>
    );
  }
}

export default App;
