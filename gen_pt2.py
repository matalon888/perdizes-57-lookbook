# Portuguese detail LAYERED ON the boho-adobe house (the two Instagram refs stay the base).
# image[0] = massing view, image[1] = exterior ref, image[2] = interior ref, image[3] = the boho render of this view.
import base64, concurrent.futures as cf, os, pathlib, requests, sys, time
KEY = os.environ["OPENAI_API_KEY"]
R = pathlib.Path(__file__).parent
import gen_ref
from gen import VIEWS
NEW = ["v11_office","v12_sitting_corner","v13_hearth_close","v14_glasswall_along","v15_dining_to_kitchen",
       "v16_from_stairs_top","e5_entrance_side","e6_pool_close","e7_side_elevation","e8_dusk_facade"]
ALL = ["e1_facade_from_pool","e2_terrace","e3_garden_corner","e4_aerial",
       "v1_living_to_pool","v4_fireplace_stairs","v5_wide_from_pool","v2_kitchen","v6_kitchen_to_living",
       "v3_dining","v7_stairs_hall","v10_corner_wide","v8_lounge_middle","v9_island_close"]

BASE = ("The FOURTH image is THE HOUSE AS ALREADY DESIGNED — keep it: the same hand-troweled white-cream lime plaster "
  "with soft rounded corners and thick organic walls, arched openings, thatch and bamboo, teak decking, warm earthy "
  "bohemian furnishing (rattan pendants, macramé, wicker, berber rugs, cream sofas, terracotta cushions, many plants). "
  "Do NOT restyle the house. Keep its materials, colours, furniture and mood. ")
ADD = {
 "boho_azulejo":
   "ADD Portuguese classical AZULEJO work into that same house: hand-painted blue-and-white azulejo panels set into the "
   "plaster — a wainscot band along one wall, a framed tile picture panel, tiled stair risers, a tiled kitchen "
   "backsplash and a tiled bench seat; outside, an azulejo panel beside the door and blue-and-white tiled steps. "
   "Blue and white against the white plaster only — everything else stays boho adobe.",
 "boho_alentejo":
   "ADD Alentejo farmhouse detail into that same house: the traditional painted border stripe in ochre-yellow (and a "
   "little indigo) running around every door, window and arch, chestnut beams with a cane (caniço) ceiling between "
   "them, glazed brown Portuguese pottery, cork and olive-wood pieces, a stone-hooded hearth detail, rush-seat wooden "
   "chairs mixed in with the existing boho furniture. The white plaster shell and boho styling stay.",
 "boho_algarve":
   "ADD Algarve Moorish detail into that same house: sea-green and sky-blue painted trim on the white plaster, latticed "
   "Algarve chimney tops and pierced plaster lattice screens, patterned hydraulic encaustic floor tiles laid as rugs "
   "within the existing floor, calçada portuguesa black-and-white cobble paving on the terrace and pool surround, "
   "Moorish lanterns, fig and citrus trees in pots. The rounded white plaster house and boho furnishing stay.",
}
INT = ("Photorealistic interior photograph, Architectural Digest quality, 24mm lens, eye level. "
 "The FIRST image is the 3D massing model — keep EXACTLY its camera angle, room geometry, wall/column/beam positions, "
 "glass openings and furniture placement. The SECOND and THIRD images are the original references for the shell and "
 "the styling. " + BASE + "{add} Scene: {scene}. Soft natural daylight, garden outside. No people, no text, no watermark.")
EXT = ("Photorealistic architectural EXTERIOR photograph, Architectural Digest quality, warm late-afternoon light. "
 "The FIRST image is the 3D massing model — keep EXACTLY its camera angle, the building's position, proportions and "
 "openings, the terrace, pool and tree positions. The SECOND and THIRD images are the original references. " + BASE +
 "{add} Scene: {scene}. Keep the second storey in the same white plaster language. No people, no text, no watermark.")

def gen(style, view):
    out = R/"out"/style/f"{view}.png"
    if out.exists(): return f"skip {style}/{view}"
    out.parent.mkdir(parents=True, exist_ok=True)
    tmpl = EXT if view.startswith("e") else INT
    prompt = tmpl.format(add=ADD[style], scene=VIEWS[view])
    for attempt in range(3):
        files = [("image[]", (f"{view}.png", open(R/"views"/f"{view}.png","rb"), "image/png")),
                 ("image[]", ("outside_ref.png", open(R/"refs/outside_ref.png","rb"), "image/png")),
                 ("image[]", ("inside_ref.png", open(R/"refs/inside_ref.png","rb"), "image/png")),
                 ("image[]", ("boho.png", open(R/"out/boho_adobe"/f"{view}.png","rb"), "image/png"))]
        r = requests.post("https://api.openai.com/v1/images/edits",
            headers={"Authorization": f"Bearer {KEY}"}, files=files,
            data={"model":"gpt-image-2","prompt":prompt,"size":"1536x1024","quality":"high","n":"1"}, timeout=900)
        if r.ok:
            out.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"])); return f"ok {style}/{view}"
        print("ERR", style, view, r.status_code, r.text[:200], flush=True); time.sleep(10)
    return f"FAIL {style}/{view}"

if __name__ == "__main__":
    args = sys.argv[1:]
    views = NEW if "--new" in args else ALL
    styles = [a for a in args if a != "--new"] or list(ADD)
    with cf.ThreadPoolExecutor(8) as ex:
        for res in ex.map(lambda a: gen(*a), [(s,v) for s in styles for v in views]): print(res, flush=True)
