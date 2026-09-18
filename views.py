import asyncio, pathlib
from playwright.async_api import async_playwright
# name: (cx,cy,cz, tx,ty,tz, fov)  sketch coords; pool wall at z=10.6, kitchen at x~9-12
VIEWS = {
 "v1_living_to_pool":   (5.2,1.45,2.9,  4.2,1.1,10.6, 72),
 "v2_kitchen":          (7.0,1.5,3.6,   11.2,0.9,8.6, 70),
 "v3_dining":           (9.9,1.5,4.6,   9.3,0.9,0.4, 74),
 "v4_fireplace_stairs": (7.2,1.5,9.2,   2.2,1.1,3.6, 70),
 "v5_wide_from_pool":   (1.4,1.6,10.1,  9.5,1.0,3.0, 75),
 "v6_kitchen_to_living":(11.2,1.55,3.2, 3.5,1.0,9.5, 75),
}
async def main():
    root = pathlib.Path(__file__).parent
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True, args=["--use-gl=angle","--enable-webgl","--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width":1536,"height":1024})
        for n,(cx,cy,cz,tx,ty,tz,f) in VIEWS.items():
            await pg.goto(f"file://{root}/scene.html?cx={cx}&cy={cy}&cz={cz}&tx={tx}&ty={ty}&tz={tz}&fov={f}")
            await pg.wait_for_function("window.__done===true", timeout=30000)
            await pg.screenshot(path=str(root/"views"/f"{n}.png"))
            print(n)
        await b.close()
asyncio.run(main())
