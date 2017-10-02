import React, { Component } from 'react';
import './App.css';

class Customers extends Component {
  constructor(props) {
    super(props);
    this.state = { customers: [] };
    var that = this;
    fetch("http://localhost:5000/tuition/customers", {credentials: 'include'})
      .then(function(response) {
        return response.json()
      }).then(function(parsed_json) {
        that.setState({customers: parsed_json})
      });
  }
  render() {
    return (
      <div className="Customers">
        {
          this.state.customers.map(
            function(customer){
              return <p>{customer.name}</p>;
            }
          )
        }
      </div>
    )
  }
}

class App extends Component {
  render() {
    return (
      <div className="App">
        <Customers/>
      </div>
    );
  }
}

export default App;
