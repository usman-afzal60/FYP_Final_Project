import React from "react";
import { Row, Col, Card } from "react-bootstrap";
import "./cardStyles.css";
import axios from "axios";
const CardComponent = (props) => {
  const handleViewReport = async () => {
    const url = `https://scanner.mailassure.tech:443/view-report/${props.id}`; // Replace with your Quart API URL
    window.open(url, "_blank");
  };
  const downloadReport = async () => {
    try {
      const response = await axios.get(
        `https://scanner.mailassure.tech:443/generate-report/${props.id}`,
        {
          responseType: "blob",
        }
      );

      const blob = new Blob([response.data], { type: "application/pdf" });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${props.id}.pdf`; // use the id to generate the file name
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Error downloading report:", err);
    }
  };
  return (
    <div>
      <Card
      // style={{ border: "1px solid #0f6c7b" }}
      >
        <Card.Header
        // style={{ backgroundColor: " #0f6c7b", color: "white" }}
        >
          {props.title}
        </Card.Header>
        <Card.Body>
          <Row>
            <Col sm={10}>
              <Card.Title>{props.subject}</Card.Title>
              <Card.Text style={{ fontWeight: "400" }}>
                Analysis Result : {props.report}
              </Card.Text>
              <button className="me-2 button" onClick={handleViewReport}>
                View Report
              </button>
              <button className="button" onClick={downloadReport}>
                Download Report
              </button>
            </Col>
            <Col sm={2}>
              {props.report === "Spam" ? (
                <div className="notificationDot notificationDot--red"></div>
              ) : (
                <div className="notificationDot notificationDot--green"></div>
              )}
              {/* <div className="notificationDot notificationDot--red"></div> */}
              {/* <div className="notificationDot notificationDot--green"></div> */}
            </Col>
          </Row>
        </Card.Body>
      </Card>
    </div>
  );
};

export default CardComponent;
