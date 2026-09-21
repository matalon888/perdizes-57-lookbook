import asyncio, pathlib
from playwright.async_api import async_playwright
# Extra angles. Sketch coords: x 0..12.1 (kitchen high x), z 0..10.6 (pool wall at z=10.6).
# Outdoor cameras sit in the garden/pool area beyond z=10.6.
VIEWS = {
 # indoor
 "v7_stairs_hall":      (6.2,1.5,6.0,   1.2,1.4,3.0,  72),   # toward staircase + elevator core
 "v8_lounge_middle":    (8.4,1.5,8.6,   5.6,0.9,2.0,  74),   # the two opened middle rooms
 "v9_island_close":     (7.4,1.5,4.0,   10.9,0.9,7.0, 72),   # kitchen island close up
 "v10_corner_wide":     (11.4,1.6,9.9,  2.0,1.0,3.5,  78),   # far corner across the whole floor
 # outdoor
 "e1_facade_from_pool": (6.4,2.3,22.6,  5.6,1.2,10.6, 60),   # from the pool looking at the house
 "e2_terrace":          (10.4,1.6,13.4, 2.0,1.3,10.8, 70),   # along the terrace, glass wall on the left
 "e3_garden_corner":    (-3.4,1.7,15.0, 7.0,1.2,9.0,  64),   # diagonal from the garden corner
 "e4_aerial":           (2.0,9.5,20.0,  6.5,0.5,9.0,  62),   # raised view over pool + house
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
