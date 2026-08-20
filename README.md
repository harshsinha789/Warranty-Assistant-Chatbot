# Warranty Assistant

An AI-powered warranty assessment application that analyzes a product image, identifies the product and visible damage, checks the warranty period, and evaluates whether the reported issue is covered under the product's warranty policy.

The application combines a React frontend, Django REST API, Gemini Vision, and Retrieval-Augmented Generation (RAG) to provide an automated warranty assessment.

---

## Features

- Upload a product or damage image
- AI-based product identification using Gemini Vision
- Detection and description of visible product damage
- Automatic product lookup from a warranty catalogue
- Warranty period validation
- Detection of expired warranties
- RAG-based warranty policy assessment
- Determines whether a reported issue is:
  - Likely Covered
  - Not Covered
  - Warranty Expired
  - Needs Verification
- Displays product information and warranty dates
- Responsive React-based user interface
- Temporary image processing without permanently storing uploaded images

---

## How It Works

The application follows this workflow:

```text
User
 │
 │ Uploads product image,
 │ purchase date and problem
 ▼
React Frontend
 │
 │ POST /api/check-warranty/
 ▼
Django REST API
 │
 ├── Gemini Vision
 │      │
 │      └── Identifies product and visible damage
 │
 ├── Product Catalogue
 │      │
 │      └── Finds product and warranty duration
 │
 ├── Warranty Checker
 │      │
 │      └── Calculates warranty expiry
 │
 └── RAG Warranty Assessment
        │
        └── Retrieves relevant warranty policy
            and evaluates the reported problem
 │
 ▼
Warranty Assessment
 │
 ├── Product information
 ├── Warranty status
 ├── Purchase date
 ├── Expiry date
 └── Coverage explanation

## Images of the working Application

1. The problems are covered under warranty
![imagealt](https://github.com/harshsinha789/Warranty-Assistant-Chatbot/blob/0ff867fc745a54e9c13ad9e10aaf826f98022458/Screenshot%202026-08-19%20193755.png)
![imagealt](https://github.com/harshsinha789/Warranty-Assistant-Chatbot/blob/0ff867fc745a54e9c13ad9e10aaf826f98022458/Screenshot%202026-08-19%20193816.png)

2. The problems are not covered under warranty
![imagealt](https://github.com/harshsinha789/Warranty-Assistant-Chatbot/blob/0ff867fc745a54e9c13ad9e10aaf826f98022458/Screenshot%202026-08-19%20194302.png)
![imagealt](https://github.com/harshsinha789/Warranty-Assistant-Chatbot/blob/0ff867fc745a54e9c13ad9e10aaf826f98022458/Screenshot%202026-08-19%20194324.png)

3. Warranty has expired
![imagealt](https://github.com/harshsinha789/Warranty-Assistant-Chatbot/blob/0ff867fc745a54e9c13ad9e10aaf826f98022458/Screenshot%202026-08-19%20194411.png)
![imagealt](https://github.com/harshsinha789/Warranty-Assistant-Chatbot/blob/0ff867fc745a54e9c13ad9e10aaf826f98022458/Screenshot%202026-08-19%20194427.png)

