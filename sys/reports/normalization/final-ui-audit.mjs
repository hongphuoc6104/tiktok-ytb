// Read-only browser audit on synthetic account/budget stores. No provider calls.
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);const {chromium}=require(process.env.VP_PLAYWRIGHT_MODULE);
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
try {
 const page=await browser.newPage({viewport:{width:1440,height:1080}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.argv[2]);await page.getByText(/Đã đọc dữ liệu/).waitFor();await page.locator('nav button').nth(1).click();
 const flow=page.locator('section.card').filter({has:page.locator('h3',{hasText:'QA Flow · flow'})});
 const colab=page.locator('section.card').filter({has:page.locator('h3',{hasText:'qa-colab · colab'})});
 const cards={flow:await flow.innerText(),colab:await colab.innerText()};
 const buttons=await page.locator('#content button').allTextContents();
 await page.screenshot({path:process.argv[3],fullPage:true});
 console.log(JSON.stringify({fixture:true,actual_browser:true,provider_calls:false,account_cards:cards,buttons,
  flow_shows_colab_hour_ring:cards.flow.includes('giờ')&&cards.flow.includes('T4'),
  flow_counts_visible_only_as_json:cards.flow.includes('"slots"'),
  setup_controls_visible:buttons.some(x=>/Khởi tạo|Mở profile|Cấu hình Flow|Cấp T4|Thu kết quả|Giải phóng/.test(x)),page_errors:errors}));
}finally{await browser.close();}
