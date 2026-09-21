# Style transfer from two Instagram reference photos onto the subsolo massing views.
# image[0] = massing view (geometry), image[1] = exterior ref, image[2] = interior ref.
import base64, concurrent.futures as cf, os, pathlib, requests, sys, time
KEY = os.environ["OPENAI_API_KEY"]
R = pathlib.Path(__file__).parent
from gen import VIEWS
VIEWS.update({
 "v7_stairs_hall": "looking across the living room toward the open floating-tread staircase and the elevator core, with the round black stove and its flue beside the stairs, exposed steel beams overhead",
 "v8_lounge_middle": "the opened-up middle rooms used as a second lounge / reading area, low sofa and small table, structural columns marking where walls were removed, daylight from both ends",
 "v9_island_close": "close view of the kitchen island and its stools with the long counter run behind it and the tall pantry wall beyond, a structural column at the right, exposed beams overhead",
 "v10_corner_wide": "very wide view from the far kitchen corner across the entire open level — island in the foreground, dining beyond, living room and the glass wall to the pool at the far end",
 "e1_facade_from_pool": "EXTERIOR: the garden facade of the house seen from across the swimming pool — the lower level opens through a long glazed wall onto a terrace, a masonry chimney block breaks the facade, mature tropical planting each side, pool water in the foreground",
 "e2_terrace": "EXTERIOR: standing on the pool terrace close to the house, looking along the glazed facade, the terrace deck running into the distance, planting and garden on the right",
 "e3_garden_corner": "EXTERIOR: three-quarter view of the house from the far garden corner, showing the glazed lower level and the terrace, lawn and tropical trees in the foreground",
 "e4_aerial": "EXTERIOR AERIAL: raised three-quarter view over the garden showing the roof, the house volume, the terrace and the swimming pool together",
})
STYLE = "boho_adobe"
VIEWS.update({
 "v11_office": "the separate office / study annex off the hall — desk facing a window, bookshelf wall, a small armchair, seen through its open doorway",
 "v12_sitting_corner": "the small sitting room in the corner by the stairs, a compact sofa and armchair against two solid walls, with the guest WC door beside it",
 "v13_hearth_close": "close view of the round free-standing stove on its stone hearth beside the staircase, its flue rising to the ceiling, seating around it",
 "v14_glasswall_along": "standing inside next to the pool glazing, looking along the length of the glass wall, the terrace and garden on one side and the living room on the other",
 "v15_dining_to_kitchen": "from the dining table looking down the length of the kitchen — island, stools and counter run leading to the tall pantry wall at the far end",
 "v16_from_stairs_top": "from the top of the staircase looking down over the whole open level — seating, the masonry fireplace on the glass wall, kitchen beyond",
 "e5_entrance_side": "EXTERIOR: the arrival side of the house seen from the driveway — two large glazed openings where the garage doors were, cobbled drive leading to the house, planting either side",
 "e6_pool_close": "EXTERIOR: low viewpoint right at the water's edge, pool surface filling the foreground and the glazed house rising behind it",
 "e7_side_elevation": "EXTERIOR: the side elevation of the house across the lawn, showing the depth of the building, the terrace edge and garden trees",
 "e8_dusk_facade": "EXTERIOR AT DUSK: the garden facade across the pool after sunset, warm interior lights glowing through the glass, lanterns lit on the terrace, deep blue sky",
})
EXT_PROMPT = (
 "Photorealistic architectural EXTERIOR photograph, Architectural Digest quality, golden afternoon light. "
 "The FIRST image is a rough 3D massing model of a São Paulo house and its garden — keep EXACTLY its camera angle, "
 "the building's position, proportions and openings, the terrace, pool and tree positions. "
 "The SECOND image is the architecture to adopt: hand-troweled white-cream lime plaster over thick organic walls with "
 "soft rounded corners, arched and rounded window openings, thatched and bamboo shade structures, warm teak decking, "
 "rough stone, Ibiza/Cycladic cave-house feel. "
 "The THIRD image is the palette and styling language: warm earthy bohemian, terracotta and clay tones, rattan, woven "
 "textures, abundant green planting. "
 "Render the massing as a finished real house exterior in that style. Scene: {scene}. "
 "Add a second storey of the same plastered language above the lower level, lush tropical São Paulo garden, "
 "realistic materials and shadows. No people, no text, no watermark."
)
PROMPT = (
 "Photorealistic interior photograph, Architectural Digest quality, 24mm lens, eye level. "
 "The FIRST image is a rough 3D massing model of a São Paulo house lower level — keep EXACTLY its camera angle, "
 "room geometry, wall/column/beam positions, glass openings and furniture placement. "
 "The SECOND image is the architectural language to adopt: hand-troweled white-cream lime plaster with soft rounded "
 "edges and thick organic walls, arched and rounded openings, thatched and bamboo ceiling elements, warm teak decking, "
 "Ibiza/Cycladic cave-house feel. "
 "The THIRD image is the decorating style to adopt: warm earthy bohemian — clay-plaster walls and ceiling in soft "
 "terracotta-beige, woven rattan pendant lamps, macramé wall hangings, wicker baskets, abundant green plants, "
 "cream slipcovered sofas with layered textured cushions, round solid-wood coffee table, patterned berber/kilim rugs, "
 "terracotta floor cushions, vintage wood chests, candles. "
 "Render the massing model's space as a finished room combining both: organic plaster architecture from image two, "
 "boho earthy decoration from image three. Scene: {scene}. "
 "Round off the hard concrete edges into soft plaster, clad or plaster the steel beams in a warm finish while keeping "
 "them where they are, and keep the glass wall to the pool and the tropical garden daylight. "
 "No people, no text, no watermark."
)
def gen(view):
    out = R/"out"/STYLE/f"{view}.png"
    if out.exists(): return f"skip {view}"
    out.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        files = [("image[]", (f"{view}.png", open(R/"views"/f"{view}.png","rb"), "image/png")),
                 ("image[]", ("outside_ref.png", open(R/"refs/outside_ref.png","rb"), "image/png")),
                 ("image[]", ("inside_ref.png", open(R/"refs/inside_ref.png","rb"), "image/png"))]
        r = requests.post("https://api.openai.com/v1/images/edits",
            headers={"Authorization": f"Bearer {KEY}"}, files=files,
            data={"model":"gpt-image-2","prompt":(EXT_PROMPT if view.startswith("e") else PROMPT).format(scene=VIEWS[view]),
                  "size":"1536x1024","quality":"high","n":"1"}, timeout=900)
        if r.ok:
            out.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"])); return f"ok {view}"
        print("ERR", view, r.status_code, r.text[:300], flush=True); time.sleep(10)
    return f"FAIL {view}"
if __name__ == "__main__":
    with cf.ThreadPoolExecutor(6) as ex:
        todo = sys.argv[1:] or list(VIEWS)
        for res in ex.map(gen, todo): print(res, flush=True)
