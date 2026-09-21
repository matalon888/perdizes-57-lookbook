import asyncio, pathlib
from playwright.async_api import async_playwright
VIEWS = {
 # indoor
 "v11_office":          (2.9,1.5,0.9,   4.4,1.0,-2.8, 76),
 "v12_sitting_corner":  (3.6,1.5,3.4,   0.8,0.9,0.8,  74),
 "v13_hearth_close":    (5.2,1.4,6.8,   2.8,1.0,4.7,  70),
 "v14_glasswall_along": (8.2,1.5,9.6,   0.6,1.1,9.9,  76),
 "v15_dining_to_kitchen":(9.6,1.5,1.2, 10.8,1.0,7.6,  74),
 "v16_from_stairs_top": (2.3,2.3,4.7,   8.2,0.9,8.2,  78),
 # outdoor
 "e5_entrance_side":    (9.2,1.8,-9.5,  9.5,1.4,0.2,  62),
 "e6_pool_close":       (5.3,0.9,18.2,  6.0,1.6,10.6, 66),
 "e7_side_elevation":   (23.0,2.4,14.5, 8.0,1.2,8.5,  58),
 "e8_dusk_facade":      (6.4,2.3,22.6,  5.6,1.2,10.6, 60),
}
async def main():
    root = pathlib.Path(__file__).parent
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        pg = await b.new_page(viewport={"width":1536,"height":1024})
        for n,(cx,cy,cz,tx,ty,tz,f) in VIEWS.items():
            await pg.goto(f"file://{root}/scene.html?cx={cx}&cy={cy}&cz={cz}&tx={tx}&ty={ty}&tz={tz}&fov={f}")
            await pg.wait_for_function("window.__done===true", timeout=30000)
            await pg.screenshot(path=str(root/"views"/f"{n}.png"))
            print(n)
        await b.close()
asyncio.run(main())
