let date = "26/11/2026 - 26/11/2026";





window.location.replace("https://fabi.ipos.vn/report/revenue/revenue/shift");
const input = document.querySelector('input[placeholder*="Chọn thời gian" i]');
if (input) {
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
  nativeSetter.call(input, date); 
  input.dispatchEvent(new Event("input", { bubbles: true }));
  input.dispatchEvent(new Event("change", { bubbles: true }));
} else {
  console.error("Input not found");
}

const btn = [...document.querySelectorAll('button[data-pc-name="button"]')].find(
  el => el.textContent.includes("Xuất báo cáo") && el.getAttribute("data-p-disabled") !== "true" && !el.disabled
);
if (btn) {
  btn.click();
} else {
  console.error("Button 'Xuất báo cáo' not found or disabled");
}
await sleep(1500);


// window.location.replace("https://fabi.ipos.vn/report/revenue/invoices/sale-by-date");
// await sleep(1500);


// window.location.replace("https://fabi.ipos.vn/report/accounting/revenue/cash-in-cash-out");
// await sleep(1500);
