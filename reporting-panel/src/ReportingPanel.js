import React, { useState, useEffect } from "react";
import { Row, Col, Dropdown } from "react-bootstrap";
import TopNav from "./Components/Nav";
import CardComponent from "./Components/Card";
import axios from "axios";


const ReportingPanel = () => {

  const [reports, setReports] = useState([]);

  useEffect(() => {
    async function fetchReports() {
      console.log("ajhbdaksdjn")
      try {
        const response = await axios.get("https://scanner.mailassure.tech:443/json_reports");
        console.log("response : ",response.data)
        setReports(response.data);
      } catch (error) {
        console.error(error);
      }
    }

    fetchReports();
  }, [reports]);
  // const arr = [
  //   {
  //     title: "Adobe Creative Cloud",
  //     subject: "Plan for your creative future",
  //     report: "Ham",
  //   },
  //   {
  //     title: "Grammarly",
  //     subject: "Get Grammarly on your phone or tablet",
  //     report: "Ham",
  //   },
  //   {
  //     title: "Tod Sacerdoti",
  //     subject: "Use AI to take notes ... without typing",
  //     report: "Spam",
  //   },
  // ];

  const [filter, setFilter] = useState("Show All");

  const filteredArr = reports.filter((value) => {
    if (filter === "Show All") {
      return true;
    }
    return value.Result === filter;
  });

  return (
    <div style={{ height: "80%" }}>
      {/* {console.log("JSON REPORTS : ",jsonReports)} */}
      {/* {<div>{console.log("data :  ",data)}</div>} */}
      {console.log("reports : ",reports)}
      <Row>
        <TopNav />
      </Row>
      <Row className="mx-5 my-3">
        <Col>
          <Dropdown
            onSelect={(selectedKey) => setFilter(selectedKey)}
            style={{
              display: "flex",
              flexDirection: "row-reverse",
            }}
          >
            <Dropdown.Toggle variant="primary" id="dropdown-basic"
            style={{ background: "#0F6C7B" }}
            >
              {filter}
            </Dropdown.Toggle>

            <Dropdown.Menu>
              <Dropdown.Item eventKey="Show All">Show All</Dropdown.Item>
              <Dropdown.Item eventKey="Ham">Ham</Dropdown.Item>
              <Dropdown.Item eventKey="Spam">Spam</Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </Col>
      </Row>
      <Row className="mx-5" style={{ marginTop: "30px" }}>
        {filteredArr.map((value, index) => (
          <div key={index} style={{ marginBottom: "10px" }}>
            <CardComponent
              id={value.ID}
              title={value.Subject}
              subject={value.Sender}
              report={value.Result}
            />
          </div>
        ))}
      </Row>
    </div>
  );
};

export default ReportingPanel;
