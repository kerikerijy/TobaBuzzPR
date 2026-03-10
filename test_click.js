const puppeteer = require('puppeteer');
(async () => {
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();
    
    page.on('console', msg => console.log('BROWSER LOG:', msg.text()));
    page.on('dialog', async dialog => {
        console.log('ALERT RECEIVED:', dialog.message());
        await dialog.dismiss();
    });
    
    await page.goto('file:///Users/yamashita.jun.kk/Antigravity/TobaBuzzPR/presentation/index.html', { waitUntil: 'load' });
    
    // Find the first map button inside tbody
    await page.evaluate(() => {
        const btn = document.querySelector('#school-table tbody tr .open-map-btn');
        if (btn) {
            console.log('Clicking button...');
            btn.click();
        } else {
            console.log('No map button found.');
        }
    });
    
    // Wait slightly
    await new Promise(r => setTimeout(r, 1000));
    
    await browser.close();
})();
