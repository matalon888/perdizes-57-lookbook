# Portuguese classical styles, interior + exterior angles, on the same massing views.
import base64, concurrent.futures as cf, os, pathlib, requests, sys, time
KEY = os.environ["OPENAI_API_KEY"]
R = pathlib.Path(__file__).parent
import gen_ref                      # loads gen.VIEWS and adds the extra angles
from gen import VIEWS
ALL_VIEWS = ["v1_living_to_pool","v2_kitchen","v3_dining","v4_fireplace_stairs","v5_wide_from_pool",
             "v6_kitchen_to_living","v7_stairs_hall","v8_lounge_middle","v9_island_close","v10_corner_wide",
             "e1_facade_from_pool","e2_terrace","e3_garden_corner","e4_aerial"]

STYLES = {
 "azulejo_pombalino":
   "LISBON POMBALINO / AZULEJO: hand-painted blue-and-white azulejo tile panels (wainscot height, and a full feature "
   "panel with a classical scene), creamy Lioz limestone floors and thresholds, dark chestnut and Brazilian rosewood "
   "joinery and coffered wood ceilings, wrought-iron balustrades and lanterns, Arraiolos wool rug, brass and glazed "
   "ceramics, tall shuttered openings — a grand 18th-century Lisbon townhouse language",
 "quinta_alentejana":
   "ALENTEJO FARMHOUSE (quinta): thick whitewashed lime walls with the signature ochre-yellow or indigo-blue painted "
   "border stripe around every opening, heavy chestnut beams, cane (canico) ceiling, terracotta tile floor, a big "
   "stone-hooded hearth, rush-seat wooden chairs, coarse linen and wool, glazed brown pottery from São Pedro do Corval, "
   "olive-wood details, cork accents, rustic honest Portuguese countryside",
 "algarve_mourisco":
   "ALGARVE MOORISH: whitewash with sky-blue and sea-green trim, latticed Algarve chimneys, horseshoe and rounded "
   "arches, patterned encaustic hydraulic floor tiles, cane-and-beam ceilings, built-in plaster benches with cushions, "
   "fig and citrus trees, calçada portuguesa cobble paving in black and white waves, Moorish lanterns, sun-bleached calm",
 "palacete_lioz":
   "LISBON PALACETE, refined classical: creamy Lioz limestone and Estremoz marble floors laid in a stone pattern, "
   "stucco mouldings and panelled walls in soft heritage tones (old rose, sage, pale gold), gilded talha dourada mirror "
   "accents, a crystal-and-brass chandelier, dark polished chestnut, Arraiolos embroidered rugs, blue-and-white "
   "porcelain, velvet and damask upholstery — Portuguese aristocratic elegance, restrained not gaudy",
}
INT = ("Photorealistic interior photograph, Architectural Digest quality, 24mm lens, eye level. "
 "Turn this rough 3D massing model into a finished real interior of a house lower level in Lisbon, Portugal. "
 "Keep EXACTLY the same camera angle, room geometry, wall/column/beam positions, glass openings and furniture placement. "
 "Scene: {scene}. Style: {style}. "
 "Ceiling 2.70 m; keep the structural beams where they are, finished to suit the style (painted, clad in wood, or "
 "plastered). Soft natural daylight through the glazing, garden outside. Real materials, realistic reflections and "
 "soft shadows, styled with books, ceramics and plants. No people, no text, no watermark.")
EXT = ("Photorealistic architectural EXTERIOR photograph, Architectural Digest quality, warm late-afternoon light. "
 "Turn this rough 3D massing model of a house and garden into a finished real house in Portugal. "
 "Keep EXACTLY its camera angle, the building's position, proportions and openings, the terrace, pool and tree positions. "
 "Scene: {scene}. Style: {style}. "
 "Add a second storey above the lower level in the same architectural language, with the roof, chimneys, window "
 "surrounds and paving that style would really use. Lush garden planting. No people, no text, no watermark.")

def gen(style, view):
    out = R/"out"/style/f"{view}.png"
    if out.exists(): return f"skip {style}/{view}"
    out.parent.mkdir(parents=True, exist_ok=True)
    tmpl = EXT if view.startswith("e") else INT
    prompt = tmpl.format(scene=VIEWS[view], style=STYLES[style])
    for attempt in range(3):
        with open(R/"views"/f"{view}.png","rb") as f:
            r = requests.post("https://api.openai.com/v1/images/edits",
                headers={"Authorization": f"Bearer {KEY}"},
                files={"image[]": (f"{view}.png", f, "image/png")},
                data={"model":"gpt-image-2","prompt":prompt,"size":"1536x1024","quality":"high","n":"1"}, timeout=900)
        if r.ok:
            out.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"])); return f"ok {style}/{view}"
        print("ERR", style, view, r.status_code, r.text[:200], flush=True); time.sleep(10)
    return f"FAIL {style}/{view}"

if __name__ == "__main__":
    styles = sys.argv[1:] or list(STYLES)
    jobs = [(s,v) for s in styles for v in ALL_VIEWS]
    with cf.ThreadPoolExecutor(8) as ex:
        for res in ex.map(lambda a: gen(*a), jobs): print(res, flush=True)
