import base64, concurrent.futures as cf, os, pathlib, requests, sys, time
KEY = os.environ["OPENAI_API_KEY"]
R = pathlib.Path(__file__).parent
VIEWS = {
 "v1_living_to_pool": "living room looking toward the floor-to-ceiling glass wall that opens to the pool terrace and garden; L-shaped sofa and coffee table in the middle, two lounge poufs by the glass, a tall masonry fireplace block built into the glass wall, a round black freestanding stove at the left edge, exposed dark steel I-beams across the ceiling",
 "v2_kitchen": "open kitchen: long counter run along the right wall, island with three stools, tall pantry wall at the far end, a slim structural column in the foreground right, exposed dark steel I-beams crossing the ceiling, glass wall to the garden at far left",
 "v3_dining": "dining area: long wooden dining table with six seats in front of two large glass panels (former garage openings) looking out to a courtyard, a slim white column between them",
 "v4_fireplace_stairs": "living room seen toward the stair side: open floating-tread staircase, a round black freestanding fireplace with a tall flue on a stone hearth beside the stairs, elevator core, L-sofa with coffee table on a rug, two armchairs, a long exposed dark steel I-beam across the ceiling",
 "v5_wide_from_pool": "wide view from the pool doors across the whole open-plan level: sofa and poufs in the foreground, round black stove and floating staircase right, kitchen with island and counter in the far background, exposed dark steel I-beam running across the ceiling",
 "v6_kitchen_to_living": "view from the kitchen back toward the living room and the glass wall to the pool: kitchen island in the right foreground, stools, a slim column, sofas beyond, masonry fireplace block built into the glass wall, garden and pool visible outside, exposed dark steel I-beams on the ceiling",
}
STYLES = {
 "green_marble_wood": "GREEN MARBLE & WOOD: deep Verde Guatemala / Verde Alpi green marble with white veining (kitchen island, counters, backsplash, fireplace cladding, dining table top), warm walnut and fluted oak joinery, oak herringbone floor, cream boucle and olive velvet upholstery, brushed brass accents, warm linear lighting",
 "calacatta_white_marble": "WHITE CALACATTA MARBLE: bookmatched Calacatta Oro marble with bold gold-grey veining on island, walls and fireplace, pale natural oak floor and cabinetry, ivory linen upholstery, brushed brass fixtures, airy luxurious and bright",
 "nero_marquina_black_marble": "BLACK MARBLE: Nero Marquina black marble with white veining on island, fireplace and feature walls, smoked oak floor and joinery, dark bronze and blackened steel, cognac leather and charcoal velvet, moody dramatic hotel-lounge lighting",
 "travertine_limestone": "TRAVERTINE: honed warm travertine for floor, island, fireplace and a sculptural coffee table, limestone plaster walls, light oak, sand and terracotta linen, rattan, olive trees in pots, relaxed Mediterranean modern",
 "breccia_rosso_marble": "BRECCIA MARBLE: bold Breccia Capraia and Rosso Levanto marble (burgundy, cream and grey clasts) on island and fireplace, cherry and dark walnut wood, terracotta and oxblood upholstery, chrome and brass, Italian mid-century modern",
 "modern_minimal": "MODERN MINIMAL: seamless light-grey microcement floor and walls, matte graphite kitchen with integrated handles, dark walnut veneer panels, black steel details, low modular sofa in stone-grey fabric, recessed linear LED coves, gallery-like contemporary architecture",
 "nordic": "NORDIC SCANDINAVIAN: white-washed wide-plank oak floor, white and pale-grey walls, light ash and birch joinery, soft wool and linen textiles in oatmeal and sage, sheepskin throws, paper pendant lamps, lots of plants, calm hygge Danish design",
}
def prompt(view, style):
    return (f"Photorealistic architectural interior photograph, Architectural Digest editorial quality, 24mm lens, eye level. "
            f"Turn this rough 3D massing model into a finished real interior of a modern São Paulo house lower level. "
            f"Keep EXACTLY the same camera angle, room geometry, wall/column/beam positions, glass openings and furniture placement as the reference. "
            f"Scene: {VIEWS[view]}. Style: {STYLES[style]}. "
            f"Ceiling 2.7 m with the steel beams kept visible and painted, soft natural daylight through the glass, lush tropical garden outside. "
            f"Real materials, realistic reflections and soft shadows, styled with books, ceramics and plants. No people, no text, no watermark.")
def gen(view, style):
    out = R/"out"/style/f"{view}.png"
    if out.exists(): return f"skip {out.name}"
    out.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        with open(R/"views"/f"{view}.png","rb") as f:
            r = requests.post("https://api.openai.com/v1/images/edits",
                headers={"Authorization": f"Bearer {KEY}"},
                files={"image[]": (f"{view}.png", f, "image/png")},
                data={"model":"gpt-image-2","prompt":prompt(view,style),"size":"1536x1024","quality":"high","n":"1"},
                timeout=600)
        if r.ok:
            out.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"])); return f"ok {style}/{view}"
        print("ERR", style, view, r.status_code, r.text[:300], flush=True); time.sleep(10)
    return f"FAIL {style}/{view}"
if __name__ == "__main__":
    only = sys.argv[1:] or list(STYLES)
    jobs = [(v,s) for s in only for v in VIEWS]
    with cf.ThreadPoolExecutor(8) as ex:
        for res in ex.map(lambda a: gen(*a), jobs): print(res, flush=True)
