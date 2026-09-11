"use strict";

(async () => {
  const { validatedPayload } = await import("../../frontend/src/services/validation.js");

  function mustThrow(label, callback) {
    try {
      callback();
    } catch {
      return;
    }
    throw new Error(`${label} did not fail validation`);
  }

  const valid = validatedPayload({
    name: "  Security   Patient  ",
    email: "security@example.test",
    password: "StrongPass123!",
    role: "patient",
    _website: ""
  }, { registration: true });
  if (valid.name !== "Security Patient") throw new Error("text normalization failed");

  const future = new Date();
  future.setDate(future.getDate() + 30);
  const futureDate = [
    future.getFullYear(),
    String(future.getMonth() + 1).padStart(2, "0"),
    String(future.getDate()).padStart(2, "0")
  ].join("-");
  const validAppointment = validatedPayload({ doctor: "Dr. Maria Santos", service: "Oral Prophylaxis", date: futureDate, time: "09:30", _website: "" });
  if (validAppointment.date !== futureDate) throw new Error("valid local appointment date was rejected");

  mustThrow("invalid calendar date", () => validatedPayload({ doctor: "Dr. Maria Santos", service: "Oral Prophylaxis", date: "2026-02-30", time: "09:30", _website: "" }));
  mustThrow("weak password", () => validatedPayload({ name: "Security Patient", email: "security@example.test", password: "weakpassword", role: "patient", _website: "" }, { registration: true }));
  mustThrow("overpayment", () => validatedPayload({ patient_id: "pat_test", treatment_date: new Date().toISOString().slice(0, 10), tooth_numbers: "11, 12", procedure: "Oral Prophylaxis", amount_charged: "500", amount_paid: "600", _website: "" }));
  mustThrow("honeypot", () => validatedPayload({ name: "Bot", rating: "5", message: "Automated feedback message", _website: "https://spam.invalid" }));

  console.log("Vue client security smoke checks passed.");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
