import React from "react";
import { Container, Row, Col, Navbar, Nav } from "react-bootstrap";
import { Link } from "react-router-dom";

const TopNav = () => {
  return (
    <div>
      <Row
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "20%",
        }}
      >
        <Navbar style={{ backgroundColor: "#0F6C7B" }} expand="sm">
          <Container>
            <Col sm={3}>
              <Link to="/" style={{ textDecoration: "none" }}>
                <Navbar.Brand>
                  <img
                    src="Logo.svg"
                    width="40"
                    height="40"
                    className="d-inline-block align-top"
                    alt="logo"
                  />
                  &nbsp;
                  <Navbar.Text style={{ fontSize: "25px", color: "white" }}>
                    MailAssure
                  </Navbar.Text>
                </Navbar.Brand>
              </Link>
            </Col>
            <Navbar.Toggle aria-controls="my-nav" />
            <Navbar.Collapse id="my-nav" className="justify-content-end">
              <Col sm={9}>
                <Nav className="me-auto ">
                  <Navbar.Text style={{ fontSize: "25px", color: "white" }}>
                    REPORTING PANEL
                  </Navbar.Text>
                </Nav>
              </Col>
              {/* <Col sm={2}>
                <Link
                  to="/logout"
                  style={{
                    display: "flex",
                    alignItems: "center",
                    textDecoration: "none",
                    color: "white",
                    // fontWeight: "bold",
                  }}
                >
                  <Navbar.Text style={{ fontSize: "25px", color: "white" }}>
                    LOGOUT
                  </Navbar.Text>

                  <div>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth="1.5"
                      stroke="currentColor"
                      className="w-2 h-2"
                      style={{
                        color: "white",
                        height: "30px",
                        width: "30px",
                      }}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75"
                      />
                    </svg>
                  </div>
                </Link>
              </Col> */}
            </Navbar.Collapse>
          </Container>
        </Navbar>
      </Row>
    </div>
  );
};

export default TopNav;
