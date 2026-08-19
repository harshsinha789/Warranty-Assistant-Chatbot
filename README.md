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

## Images of the Working Application

<img width="1560" height="887" alt="image" src="https://github.com/user-attachments/assets/c5791f31-a8c1-4aa4-a33a-6224ed6b2bf1" />
<img width="1371" height="810" alt="image" src="https://github.com/user-attachments/assets/5c2c7af9-2c07-4837-9a20-065bcf70c219" />

<img width="1328" height="875" alt="image" src="https://github.com/user-attachments/assets/1cf98940-1174-4860-af05-90e2be36c950" />
<img width="1313" height="826" alt="image" src="https://github.com/user-attachments/assets/f6a1fc50-4448-4c90-9a2d-3ab959856cb2" />

<img width="1277" height="872" alt="image" src="https://github.com/user-attachments/assets/95378ae8-f90f-4eb1-a8a2-f866e1367748" />
<img width="1272" height="782" alt="image" src="https://github.com/user-attachments/assets/e7394394-d897-4f44-8d95-cfcb5ecf7cb5" />


