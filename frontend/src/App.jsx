import { useState } from "react";
import "./App.css";

function App() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [purchaseDate, setPurchaseDate] = useState("");
  const [problem, setProblem] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  
  const handleReset = () => {
  setImage(null);
  setPreview(null);
  setPurchaseDate("");
  setProblem("");
  setResult(null);
  setError("");
};

  const handleImageChange = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    setImage(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setResult(null);

    if (!image) {
      setError("Please upload a product image.");
      return;
    }

    if (!purchaseDate) {
      setError("Please enter the purchase date.");
      return;
    }

    if (!problem.trim()) {
      setError("Please describe the problem.");
      return;
    }

    const formData = new FormData();

    formData.append("image", image);
    formData.append("purchase_date", purchaseDate);
    formData.append("problem", problem);

    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/check-warranty/",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message ||
          data.error ||
          "Something went wrong."
        );
      }

      setResult(data);

    } catch (err) {
      setError(
        err.message ||
        "Unable to connect to the warranty service."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">

      <header className="header">
        <h1>Warranty Assistant</h1>
        <p>
          AI-powered warranty assessment
        </p>
      </header>

      <main className="container">

        <form
          className="warranty-form"
          onSubmit={handleSubmit}
        >

          {/* Image Upload */}

          <section className="form-section">

            <h2>Product Image</h2>

            <p className="section-description">
              Upload a clear image of the product or
              the visible damage.
            </p>

            <label className="upload-box">

              {preview ? (
                <img
                  src={preview}
                  alt="Product preview"
                  className="image-preview"
                />
              ) : (
                <div className="upload-placeholder">
                  <span className="upload-icon">📷</span>

                  <strong>
                    Click to upload an image
                  </strong>

                  <span>
                    JPG, PNG or WEBP
                  </span>
                </div>
              )}

              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleImageChange}
                hidden
              />

            </label>

          </section>


          {/* Purchase Date */}

          <section className="form-section">

            <label htmlFor="purchase-date">
              Purchase Date
            </label>

            <input
              id="purchase-date"
              type="date"
              value={purchaseDate}
              onChange={(e) =>
                setPurchaseDate(e.target.value)
              }
              max={new Date().toISOString().split("T")[0]}
              className="input"
            />

          </section>


          {/* Problem */}

          <section className="form-section">

            <label htmlFor="problem">
              Describe the Problem
            </label>

            <textarea
              id="problem"
              value={problem}
              onChange={(e) =>
                setProblem(e.target.value)
              }
              placeholder="For example: The screen is cracked and not working."
              rows="5"
              className="input textarea"
            />

          </section>


          {/* Error */}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}


          {/* Submit */}

          <button
            type="submit"
            className="check-button"
            disabled={loading}
          >

            {loading
              ? "Checking Warranty..."
              : "Check Warranty"}

          </button>

        </form>


        {/* Loading */}

        {loading && (
          <div className="loading">

            <div className="spinner"></div>

            <p>
              Analyzing your product and warranty...
            </p>

            <span>
              This may take a few seconds.
            </span>

          </div>
        )}


        {/* Result */}

        {result && !loading && (

          <section className="result-card">

            <h2>Warranty Assessment</h2>


            {/* Status */}

            <div
              className={`status ${result.status
                ?.toLowerCase()
                .replace("_", "-")}`}
            >

              {result.status === "NOT_COVERED" && (
                <>🔴 Not Covered</>
              )}

              {result.status === "LIKELY_COVERED" && (
                <>🟢 Likely Covered</>
              )}

              {result.status === "ACTIVE" && (
                <>🟢 Warranty Active</>
              )}

              {result.status === "EXPIRED" && (
                <>🔴 Warranty Expired</>
              )}

              {result.status === "NEEDS_VERIFICATION" && (
                <>🟡 Needs Verification</>
              )}

            </div>


            {/* Product */}

            {result.product && (
              <div className="product-info">

                <h3>Product</h3>

                <p>
                  <strong>Brand:</strong>{" "}
                  {result.product.brand}
                </p>

                <p>
                  <strong>Product:</strong>{" "}
                  {result.product.product}
                </p>

                <p>
                  <strong>Model:</strong>{" "}
                  {result.product.model}
                </p>

              </div>
            )}


            {/* Dates */}

            {(result.purchase_date ||
              result.expiry_date) && (

              <div className="warranty-info">

                {result.purchase_date && (
                  <p>
                    <strong>Purchase Date:</strong>{" "}
                    {result.purchase_date}
                  </p>
                )}

                {result.expiry_date && (
                  <p>
                    <strong>Warranty Expiry:</strong>{" "}
                    {result.expiry_date}
                  </p>
                )}

              </div>
            )}


            {/* Message */}

            {result.message && (
  <div className="assessment">

    <p>
      {result.message
        .replace(
          /^(🟢 Likely Covered|🔴 Not Covered|🟡 Needs Verification|🔴 Warranty Expired)\s*/,
          ""
        )
        .trim()}
    </p>

  </div>
)}

{/* New Assessment */}

<button
  type="button"
  className="reset-button"
  onClick={handleReset}
>
  ↻ New Assessment
</button>

          </section>
        )}

      </main>

    </div>
  );
}

export default App;