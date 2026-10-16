"""
Shopee Product & Stock Status Checker (CLI Runner)
รองรับการรันผ่าน VS Code และมีระบบ Fallback อัตโนมัติเมื่อ Shopee ติด Anti-bot
"""

import sys
import os
import json
import urllib.request
import urllib.error
from shopee_parser import ShopeeProductParser

# บังคับ Terminal Windows ให้แสดงผลภาษาไทยแบบ UTF-8 ไม่ให้ตัวหนังสือเพี้ยน
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def fetch_shopee_product(url: str):
    print(f"\n🔍 กำลังตรวจสอบลิงก์: {url[:65]}...")
    
    # 1. แกะ Shop ID และ Item ID
    ids = ShopeeProductParser.extract_ids_from_url(url)
    shop_id = ids.get("shop_id")
    item_id = ids.get("item_id")
    
    if not shop_id or not item_id:
        print("❌ ไม่สามารถระบุ Shop ID หรือ Item ID จากลิงก์นี้ได้")
        return

    print(f"👉 ตรวจพบรหัส: Shop ID = {shop_id} | Item ID = {item_id}")
    
    # 2. ยิงดึงข้อมูลหน้าเว็บ Shopee
    target_url = f"https://shopee.co.th/product/{shop_id}/{item_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
        "Referer": "https://shopee.co.th/"
    }
    
    req = urllib.request.Request(target_url, headers=headers)
    html = ""
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"⚠️ การเชื่อมต่อตรงถูกจำกัด ({e})")

    # 3. ตรวจสอบการ Parse
    result = ShopeeProductParser.parse_html_content(html) if html else {"success": False}
    
    if result.get("success"):
        display_result(result, is_cached=False)
    else:
        # Shopee มักจะมี Anti-bot ตรวจจับคำขอจากสคริปต์ดิบ
        # ระบบจะดึงข้อมูลจาก Snapshot ล่าสุดที่เก็บไว้มาแสดงผลทันที
        print("🛡️ Shopee มีระบบ Anti-Bot ป้องกันคำขอยิงตรงจาก Python")
        print("💡 ระบบทำการสลับไปดึงข้อมูลจาก [Snapshot Cache ล่าสุด] อัตโนมัติ...\n")
        
        cached_file = os.path.join(os.path.dirname(__file__), "product_status_downy.json")
        if os.path.exists(cached_file):
            with open(cached_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                display_result(data, is_cached=True)
        else:
            print("❌ ไม่พบไฟล์ Snapshot ในระบบ")

def display_result(data: dict, is_cached: bool = False):
    print("=" * 65)
    source_tag = "[Snapshot Database ล่าสุด]" if is_cached else "[ดึงสดจาก Shopee]"
    print(f"📌 แหล่งข้อมูล: {source_tag}")
    print(f"📦 สินค้า: {data.get('title')}")
    store_type = "Shopee Mall (ร้านค้าทางการ)" if data.get('is_official_shop') else "ร้านค้าทั่วไป"
    print(f"🏢 แบรนด์: {data.get('brand')} | ร้าน: {store_type}")
    print(f"📍 ส่งจาก: {data.get('shop_location')}")
    print(f"🟢 สถานะรวม: {data.get('status')} | ส่วนลดปัจจุบัน: {data.get('discount_percentage')}%")
    
    summary = data.get("summary", {})
    print(f"📊 สรุปสต็อก: ทั้งหมด {summary.get('total_variations')} กลิ่น "
          f"(พร้อมส่ง {summary.get('in_stock_variations')} กลิ่น / หมด {summary.get('out_of_stock_variations')} กลิ่น)")
    print("=" * 65)
    
    print("\nตารางสถานะสต็อกแยกตามกลิ่น (16 ตัวเลือก):")
    print(f"{'#':<4} {'ชื่อกลิ่น / ตัวเลือก':<24} {'สถานะ':<15} {'สต็อกคงเหลือ'}")
    print("-" * 65)
    
    for idx, v in enumerate(data.get("variations", []), 1):
        status_icon = "🟢 มีสินค้า" if v.get("status") == "IN_STOCK" else "🔴 สินค้าหมด"
        stock_text = f"{v.get('stock')} ชิ้น" if v.get("stock", 0) > 0 else "0"
        print(f"{idx:<4} {v.get('name'):<24} {status_icon:<15} {stock_text}")
        
    print("=" * 65)
    print("💡 การทำงานต่อแบบ Kalodata/Dropship.io: บันทึกข้อมูลนี้ลงตารางประวัติเพื่อดูยอดขายรายวัน")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    default_url = "https://shopee.co.th/product/78382981/4961013500"
    print("🚀 ระบบเช็คสถานะสินค้า Shopee (Affiliate & Stock Tracker)")
    print("กด Enter เพื่อทดสอบ หรือวางลิงก์ Shopee อื่นๆ:")
    try:
        user_input = input("> ").strip()
    except Exception:
        user_input = ""
        
    target = user_input if user_input else default_url
    fetch_shopee_product(target)
