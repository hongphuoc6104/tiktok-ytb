// Isolated browser reads only local fixture HTTP. Never user's profile/providers.
import fs from 'node:fs';
import {chromium} from 'playwright';
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
try {
 const page=await browser.newPage({viewport:{width:1280,height:1100}});
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 await page.goto(process.argv[2]);await page.getByText(/Đã đọc dữ liệu/).waitFor();
 await page.locator('nav button').nth(1).click();
 const flow=page.locator('[data-service="flow"]'),colab=page.locator('[data-service="colab"]');
 if(await flow.count()!==1||await colab.count()!==2)throw Error('Fixture accounts were not rendered');
 const flowText=await flow.innerText();const colabText=await colab.first().innerText();
 if(!flowText.includes('3/150')||!flowText.includes('Chưa rõ kết quả: 3'))throw Error('Flow count/unknown state missing');
 if(await flow.locator('.ring').count())throw Error('Flow rendered a time ring');
 if(!colabText.includes('nội bộ'))throw Error('Internal Colab budget qualifier missing before allocation');
 if(!flowText.includes('không phải quota Google'))throw Error('Flow internal counter qualifier missing');
 if(await page.getByLabel('Quyền setup',{exact:true}).count()!==1)throw Error('Setup authority selector missing');
 if(await page.getByLabel('Chỉ dẫn setup nguyên văn',{exact:true}).count()!==1)throw Error('Actual setup source field missing');
 await page.screenshot({path:process.argv[4],fullPage:true});
 fs.writeFileSync(process.argv[3],JSON.stringify({fixture:true,live_provider:false,flow_ring_count:await flow.locator('.ring').count(),colab_ring_count:await colab.locator('.ring').count(),flow_counter:'3/150',unknown_count:3,errors,screenshot:process.argv[4]},null,2));
 if(errors.length)throw Error(errors.join(';'));
} finally {await browser.close();}
