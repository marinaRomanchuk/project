import React, { Component } from 'react'
import logo from './logo.svg';
import { useState } from "react";
import format from "date-fns/format";
import getDay from "date-fns/getDay";
import parse from "date-fns/parse";
import startOfWeek from "date-fns/startOfWeek";
import './App.css';
import CustomModal from './components/Modal'
import Modal from "./components/Modal";
import axios from "axios";
import { Calendar, dateFnsLocalizer } from "react-big-calendar";
import "react-big-calendar/lib/css/react-big-calendar.css";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

const locales = {
    "ru": require("date-fns/locale/ru"),
};

const localizer = dateFnsLocalizer({
    format,
    parse,
    startOfWeek,
    getDay,
    locales,
});

const events = [
    {
        title: "Big Meeting",
        allDay: true,
        start: "2021-11-01",
        end: "2021-11-07",
        //start: new Date(2021, 6, 0),
        //end: new Date(2021, 6, 0),
    },
    {
        title: "Vacation",
        start: new Date(2021, 6, 7),
        end: new Date(2021, 6, 10),
    },
    {
        title: "Conference",
        start: new Date(2021, 6, 20),
        end: new Date(2021, 6, 23),
    },
];

class App extends Component {

    constructor(props) {
        super(props);
        this.state = {
            viewCompleted: false,
            activeItem: {
                title: "",
                description: "",
                completed: false
            },
            taskList: [],
            event: [],
        };
    }

    // Add componentDidMount()
    componentDidMount() {
        this.refreshList();
    }


    refreshList = () => {
        axios   //Axios to send and receive HTTP requests
            .get("http://localhost:8000/api/tasks/")
            .then(res => this.setState({ taskList: res.data }))
            .catch(err => console.log(err));

    };



    displayCompleted = status => {
        if (status) {
            return this.setState({ viewCompleted: true });
        }
        return this.setState({ viewCompleted: false });
    };


    renderTabList = () => {
        return (
            <div className="my-5 tab-list">
        <span
            onClick={() => this.displayCompleted(true)}
            className={this.state.viewCompleted ? "active" : ""}
        >
          Completed
            </span>
                <span
                    onClick={() => this.displayCompleted(false)}
                    className={this.state.viewCompleted ? "" : "active"}
                >
          Incompleted
            </span>
            </div>
        );
    };

    // Main variable to render items on the screen
    renderItems = () => {
        const { viewCompleted } = this.state;
        const newItems = this.state.taskList.filter(
            item => item.completed === viewCompleted
        );
        return newItems.map(item => (
            <li
                key={item.id}
                className="list-group-item d-flex justify-content-between align-items-center"
            >
        <span
            className={`todo-title mr-2 ${this.state.viewCompleted ? "completed-todo" : ""
            }`}
            title={item.description}
        >
          {item.title}
        </span>
                <span>
          <button
              onClick={() => this.editItem(item)}
              className="btn btn-info text-white mr-2"
          >
            Edit
          </button>
          <button
              onClick={() => this.handleDelete(item)}
              className="btn btn-danger mr-2"
          >
            Delete
          </button>
        </span>
            </li>
        ));
    };

    toggle = () => {
        this.setState({ modal: !this.state.modal });
    };

    handleSubmit = item => {
        this.toggle();
        if (item.id) {
            // if old post to edit and submit
            axios
                .put(`http://localhost:8000/api/tasks/${item.id}/`, item)
                .then(res => this.refreshList());
            return;
        }
        // if new post to submit
        axios
            .post("http://localhost:8000/api/tasks/", item)
            .then(res => this.refreshList());
    };

    // Delete item
    handleDelete = item => {
        axios
            .delete(`http://localhost:8000/api/tasks/${item.id}/`)
            .then(res => this.refreshList());
    };
    // handleDelete = item => {//add this after modal creation
    //   alert("delete" + JSON.stringify(item));//add this after modal creation
    // };

    // Create item
    createItem = () => {
        const item = { title: "", description: "", completed: false };
        this.setState({ activeItem: item, modal: !this.state.modal });
    };

    //Edit item
    editItem = item => {
        this.setState({ activeItem: item, modal: !this.state.modal });
    };


    // -I- Start by visual effects to viewer
    render() {
        return (
            <main className="content p-3 mb-2 bg-info">
                <h1 className="text-white text-uppercase text-center my-4">Task Manager</h1>
                <div className="row ">
                    <div className="col-md-6 col-sm-10 mx-auto p-0">
                        <div className="card p-3">
                            <div className="">
                                <button onClick={this.createItem} className="btn btn-warning">
                                    Add task
                                </button>
                            </div>
                            {this.renderTabList()}
                            <ul className="list-group list-group-flush">
                                {this.renderItems()}
                            </ul>
                        </div>
                    </div>
                    <Calendar localizer={localizer} events={this.state.taskList} startAccessor="start" endAccessor="end" style={{ height: 800, margin: "80px" }} />
                </div>
                <footer className="my-5 mb-2 bg-info text-white text-center">
                    Minsk, Fall 2021
                </footer>
                {this.state.modal ? (
                    <Modal
                        activeItem={this.state.activeItem}
                        toggle={this.toggle}
                        onSave={this.handleSubmit}
                    />
                ) : null}
            </main>
        );
    }
}
export default App;