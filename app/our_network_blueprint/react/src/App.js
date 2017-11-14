import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import './App.css';
import { createStore } from 'redux'
import { Provider, connect } from 'react-redux'

const School = state => {
  return (
    <div className="row school">
      <div className="col-md-2">
        <a href={state.websiteUrl} target="_blank" rel="noopener noreferrer">
          <img src={state.logoUrl} alt="" data-recalc-dims="1" />
        </a>
      </div>
      <div className="col-md-8">
        <a href={state.websiteUrl} target="_blank" rel="noopener noreferrer">{state.name}</a><br />
        Ages {state.ages}<br />
        {state.address}<br />
        {state.email.map(
          (e, index) => (
            <div key={index}>
              {e.name}&nbsp;
              <a href={"mailto:" + e.address}><i className="fa fa-envelope">X</i></a>
            </div>
          )
        )}
      </div>
    </div>
  )
}

const Hub = state => {
  return (
    <div id="cambridge-ma" className="hub-container">
      <div className="row hub">
        <div className="col-md-12">
          <h3 style={{marginBottom: "0px"}}>{ state.name }</h3>
          <p style={{marginBottom: "24px"}}>If you are interested in applying to a school in { state.name }, <a href={state.applicationUrl}>click here</a> to start your application.</p>
        </div>
      </div>
      {state.schools.map((school, index) => (<School key={index} {...school} />))}
    </div>
  )
}

class Map extends Component {
  render() {
    return (
      <div>
        Map
      </div>
    )
  }
}

const mapStateToProps = state => {
  return {
    hubs: state
  }
}

const mapDispatchToProps = dispatch => {
  return {
    // TBD
  }
}

const List = connect(
  mapStateToProps,
  mapDispatchToProps
)(state => {
  return (
    <div>
      {state.hubs.map((hub, index) => (<Hub key={index} {...hub} />))}
    </div>
  )
})

const SET_STATE = 'SET_STATE'

function updateState(state) {
  return {
    type: SET_STATE,
    state
  }
}

var reducer = (state, action) => {
  switch(action.type) {
    case SET_STATE:
      return state;
    default:
      return state;
  }
}

var store = createStore(
  reducer,
  [
    {
      "name": "Cambridge",
      "applicationUrl": "https://TBD",
      "schools": [
        {
          "name": "Aster",
          "websiteUrl": "http://astermontessori.org/",
          "logoUrl": "https://i2.wp.com/media.wildflowerschools.net/wp-content/uploads/sites/13/2017/02/aster-logo-200w.png?w=1080",
          "ages": "3-6",
          "address": "883 Cambridge St, Cambridge, MA 02141",
          "email": [
            {
              "name": "Angelina",
              "address": "angelina@astermontessori.org"
            }
          ]
        }
      ]
    }
  ]
);

setTimeout(function(){
  ReactDOM.render(
    <Provider store={store}>
      <List />
    </Provider>, document.getElementById('list')
  );

  ReactDOM.render(
    <Provider store={store}>
      <Map />
    </Provider>,
    document.getElementById('map')
  );
}, 200);
