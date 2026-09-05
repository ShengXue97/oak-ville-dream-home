# Bedroom 3 layout correction

The earlier arrangement was too congested: the desk stool overlapped the bed
and the foot gap was approximately 265 mm. Passing selected corridor routes
did not validate every approach to the bed. The new dedicated checks cover
the bed/stool overlap and the intended bedroom circulation.

The correction is saved in `oak-ville.blend`, its construction scripts, and
the Unreal export. Room walls have not moved. The plan labels the bedroom
bay width as 3000 mm; the model's 3350 mm partition depth is still inferred
from the photographed plan, not a written site measurement. The Japandi tour
image establishes room relationships but cannot establish scale from its lens.

The proposed mattress is now a 900 × 1900 mm single, centred at plan coordinates
(5.60, 1.20) m. The wardrobe sits against the west side; the desk and tucked
stool sit at the foot end. The measured model gaps are 615 mm between bed and
desk and 1033 mm between wardrobe fronts and the accessible bedside. These are
design choices, not regulatory compliance claims. The narrow wall side is not
intended for access. Confirm actual furniture sizes, joinery thicknesses and
door operation with the designer before fabrication.

The bedroom door is hinged at the central-partition jamb and opens into the
room. Its 86-degree stop keeps the attached handle clear of the partition.
The W05 inspection route passes through the doorway, around the bed foot and
along the accessible side. Dimensions and results are in
`validation/bedroom3-clearances.json`; the component schedule and dimensioned
SVG are regenerated from Blender.

An accidental 1.2645× whole-scene transform was detected by the reproduction
comparison and restored with the owner's approval. A temporary backup remains
under `.cache/before-scale-review.blend`; it is not the dimensioned deliverable.
