import puppeteer from "puppeteer";
import HAR from "puppeteer-har";
import fs from "fs";

(async () => {
  // read csv file and get the domain
  const csv = fs.readFileSync("data/majestic_million.csv", "utf8");
  const lines = csv.split("\n");
  const domains = lines.map((line) => {
    const parts = line.split(",");
    return parts[2];
  });
  // console.log(domains);
  domains.shift(); // remove the header

  const browser = await puppeteer.launch({
    headless: true,
  });
  const page = await browser.newPage();

  // await page.tracing.start({
  //   categories: ["cpu", "gc", "heap"],
  //   categoryNamePatterns: ["*"],
  // });
  for (let i = 0; i < 10; i++) {
    const domain = domains[i];
    // console.log(domain);
    await page.tracing.start({
      // path: `trace-${domain}.json`,
      // categories: ["net", "netlog", "cast.mdns", "cpu", "ipc", "renderer"],
    });
    const har = new HAR(page);
    await har.start({ path: `traces/${domain}.har` });

    // await page.setRequestInterception(true);
    // await page.on("request", (request) => {
    //   request.continue();
    // });
    // await page.on("response", (response) => {
    //   console.log(
    //     `Received response: ${response.status()}\t${JSON.stringify(
    //       response.timing()
    //     )}`
    //   );
    // });

    // await page.goto("setu.co/");
    await page.goto("https://" + domain);

    // await page.click('button#myButton');
    // await page.waitForNavigation();
    // await new Promise((r) => setTimeout(r, 2000));

    // time to first byte
    const ttfb = await page.evaluate(() => {
      const timing = performance.getEntriesByType("navigation")[0];
      return timing.responseStart - timing.requestStart;
    });

    console.log(`${domain}\t\t${ttfb}ms`);

    await page.tracing.stop();
    await har.stop();
  }
  // await page.click('button#myButton');

  // const networkData = await page.on("request", (request) => {
  //   return request.abort();
  // });

  // fs.writeFileSync("network-trace.json", JSON.stringify(networkData));

  await browser.close();
})();
