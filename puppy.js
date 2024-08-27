// import puppeteer from 'puppeteer';
// // Or import puppeteer from 'puppeteer-core';

// // Launch the browser and open a new blank page
// const browser = await puppeteer.launch();
// const page = await browser.newPage();

// // Navigate the page to a URL.
// await page.goto('https://developer.chrome.com/');

// // Set screen size.
// await page.setViewport({width: 1080, height: 1024});

// // Type into search box.
// await page.locator('.devsite-search-field').fill('automate beyond recorder');

// // Wait and click on first result.
// await page.locator('.devsite-result-item-link').click();

// // Locate the full title with a unique string.
// const textSelector = await page
//   .locator('text/Customize and automate')
//   .waitHandle();
// const fullTitle = await textSelector?.evaluate(el => el.textContent);

// // Print the full title.
// console.log('The title of this blog post is "%s".', fullTitle);

// await browser.close();

import puppeteer from "puppeteer";
import HAR from "puppeteer-har";
import fs from "fs";

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
  });
  const page = await browser.newPage();

  // await page.tracing.start({
  //   categories: ["cpu", "gc", "heap"],
  //   categoryNamePatterns: ["*"],
  // });
  await page.tracing.start({
    path: "trace.proto",
    // categories: ["net", "netlog", "cast.mdns", "cpu", "ipc", "renderer"],
  });
  const har = new HAR(page);
  await har.start({ path: "trace-net.har" });

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

  await page.goto("https://setu.co/");

  // await page.click('button#myButton');
  // await page.waitForNavigation();
  // await new Promise((r) => setTimeout(r, 2000));

  // time to first byte
  const ttfb = await page.evaluate(() => {
    const timing = performance.getEntriesByType("navigation")[0];
    return timing.responseStart - timing.requestStart;
  });

  console.log(`Time to first byte: ${ttfb}ms`);

  await page.tracing.stop();
  await har.stop();

  // await page.click('button#myButton');

  // const networkData = await page.on("request", (request) => {
  //   return request.abort();
  // });

  // fs.writeFileSync("network-trace.json", JSON.stringify(networkData));

  await browser.close();
})();
