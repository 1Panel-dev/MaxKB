function format(decimal?: number, digits?: number): string | undefined {
  if (digits == undefined) {
    digits = 0;
  }
  return decimal?.toLocaleString("zh-CN", {
    style: "decimal",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

const util = {
  format,
};

export default util;
