"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const {classifyBloodPressure: classify} = require("./app.js");

function screening(systolic, diastolic, symptoms = "no", pregnancy = "no") {
  return classify({systolic, diastolic, symptoms, pregnancy});
}

test("severe criterion is strictly >180 OR >120, not an AND", () => {
  assert.equal(screening(181, 80).code, "severe");
  assert.equal(screening(160, 121).code, "severe");
  assert.equal(screening(180, 120).code, "below");
});

test("possible organ injury is urgent, even below the severe threshold", () => {
  assert.equal(screening(195, 125, "yes").code, "emergency");
  assert.equal(screening(145, 95, "yes").code, "emergency");
});

test("not assessed is not treated as absence of injury", () => {
  assert.equal(screening(190, 90, "uncertain").code, "uncertain");
  assert.equal(screening(130, 80, "uncertain").code, "uncertain");
});

test("pregnancy and postpartum bypass the adult nonpregnant pathway", () => {
  assert.equal(screening(175, 112, "no", "yes").code, "special");
  assert.equal(screening(125, 85, "no", "yes").code, "special");
});

test("reject malformed, non-finite, negative, reversed and unrealistic BP", () => {
  for (const [s, d] of [["", "90"], ["Infinity", "90"], [90, 110],
    [-1, 90], [401, 90], [130, 301], ["abc", 70], [120.5, 80]]) {
    assert.equal(screening(s, d).code, "invalid", String(s) + "/" + String(d));
  }
});

test("reject missing context rather than silently default", () => {
  assert.equal(screening(125, 80, "none").code, "invalid");
  assert.equal(screening(125, 80, "no", "").code, "invalid");
});

test("output messages avoid diagnosing absence of target-organ injury", () => {
  const result = screening(198, 128, "no");
  assert.match(result.summary, /does not establish/);
  assert.match(result.action, /clinical evaluation/);
});
