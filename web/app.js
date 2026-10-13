"use strict";

/**
 * Educational screening logic, not a diagnosis or a treatment protocol.
 * AHA/ACC 2025: SBP >180 OR DBP >120 with acute target-organ injury
 * is a hypertensive emergency; the injury cannot be assessed by BP alone.
 */
function classifyBloodPressure(input) {
  const rawSbp = String(input.systolic ?? "").trim();
  const rawDbp = String(input.diastolic ?? "").trim();
  const sbp = Number(rawSbp);
  const dbp = Number(rawDbp);
  if (!rawSbp || !rawDbp || !Number.isFinite(sbp) || !Number.isFinite(dbp) ||
      !Number.isInteger(sbp) || !Number.isInteger(dbp) ||
      sbp < 1 || sbp > 400 || dbp < 1 || dbp > 300 || sbp <= dbp) {
    return {code: "invalid", title: "Check the measurements",
      summary: "Enter plausible whole-number systolic and diastolic values in mm Hg (systolic must exceed diastolic).",
      action: "Correct the values before continuing."};
  }

  const symptoms = input.symptoms;
  if (!["yes", "no", "uncertain"].includes(symptoms)) {
    return {code: "invalid", title: "Complete the symptom assessment",
      summary: "Select whether concerning symptoms or suspected acute organ injury are present.",
      action: "Select an option before continuing."};
  }
  if (!["yes", "no"].includes(input.pregnancy)) {
    return {code: "invalid", title: "Complete the context",
      summary: "Indicate whether the pregnancy/postpartum pathway may apply.",
      action: "Select an option before continuing."};
  }

  const severe = sbp > 180 || dbp > 120;
  const bp = sbp + "/" + dbp + " mm Hg";

  if (input.pregnancy === "yes") {
    return {code: "special", title: "Pregnancy/postpartum: separate assessment required",
      summary: bp + ". Pregnancy and the postpartum period have distinct urgent hypertension criteria, which this nonpregnant-adult pathway does not evaluate.",
      action: "Seek prompt obstetric assessment. If symptoms suggest acute illness, seek emergency care now."};
  }
  if (symptoms === "yes") {
    return {code: "emergency", title: "Possible acute emergency",
      summary: bp + ". Concerning symptoms or suspected organ injury need immediate assessment. " +
        (severe ? "This exceeds the severe BP threshold; hypertensive emergency is possible, but not confirmed." :
          "A BP below the severe threshold does not exclude another emergency."),
      action: "Seek emergency medical care now. Do not attempt rapid unsupervised BP reduction."};
  }
  if (severe && symptoms === "uncertain") {
    return {code: "uncertain", title: "Severe blood pressure — organ injury unknown",
      summary: bp + " exceeds SBP 180 or DBP 120 mm Hg. An emergency cannot be ruled out without clinical assessment.",
      action: "Arrange urgent clinical assessment. Emergency care is indicated if concerning symptoms occur."};
  }
  if (severe) {
    return {code: "severe", title: "Severe blood pressure — no concerning symptoms reported",
      summary: bp + " exceeds SBP 180 or DBP 120 mm Hg. Symptom absence does not establish that acute target-organ damage is absent.",
      action: "Repeat the measurement correctly and seek timely clinical evaluation. Do not rapidly lower BP without clinical supervision."};
  }
  if (symptoms === "uncertain") {
    return {code: "uncertain", title: "Assessment incomplete",
      summary: bp + " is below the severe BP threshold, but possible acute organ injury has not been assessed.",
      action: "Contact a clinician for assessment; seek emergency care for concerning symptoms."};
  }
  return {code: "below", title: "Below the severe BP threshold",
    summary: bp + " does not cross the AHA/ACC severe BP threshold. This is not a diagnosis of normal blood pressure or absence of disease.",
    action: "Follow routine BP assessment and follow-up guidance. Seek urgent care if new concerning symptoms develop."};
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {classifyBloodPressure};
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("bp-form");
    const result = document.getElementById("result");
    if (!form || !result) return;
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      const selected = form.querySelector('input[name="symptoms"]:checked');
      const answer = classifyBloodPressure({
        systolic: form.elements.systolic.value,
        diastolic: form.elements.diastolic.value,
        pregnancy: form.elements.pregnancy.value,
        symptoms: selected ? selected.value : ""
      });
      result.dataset.state = answer.code;
      result.hidden = false;
      document.getElementById("result-heading").textContent = answer.title;
      document.getElementById("result-summary").textContent = answer.summary;
      document.getElementById("result-action").textContent = answer.action;
      result.focus();
    });
  });
}
