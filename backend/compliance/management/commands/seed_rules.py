from django.core.management.base import BaseCommand
from django.db import transaction

from compliance.models import CommodityCategory, Exemption, Rule, ScheduleEntry, StandardPackSize

SOURCE = "The Legal Metrology (Package Commodities) Rules, 2011.pdf"

RULES = [
    ("3", "Applicability of Chapter II", "Chapter II does not apply to packages over 25 kg/25 litres, except cement and fertilizer bags up to 50 kg, or packages intended for industrial or institutional consumers.", "APPLICABILITY", "MANUAL_REVIEW", 4),
    ("4", "Pre-packing and declarations", "A commodity must not be pre-packed for sale, distribution or delivery unless required declarations appear on the package or securely affixed label.", "DECLARATION_SET", "FAIL", 4),
    ("5", "Standard package sizes", "Commodities specified in the Second Schedule must be packed in the specified standard quantities; the PDF notes the non-standard-pack wording provision was withdrawn from 01.07.2012.", "STANDARD_PACK_SIZE", "WARNING", 5),
    ("6", "Declarations on every package", "Required declarations include identity and address, commodity name, net quantity, manufacture/pre-packing/import month and year, retail sale price, relevant dimensions and consumer complaint contact details, subject to the rule's provisos.", "DECLARATION_SET", "FAIL", 5),
    ("7", "Principal display panel and numeral height", "Principal display panel and minimum numeral heights depend on quantity, area and declaration form; supplied images cannot establish physical size reliably without calibration.", "DISPLAY_MEASUREMENT", "MANUAL_REVIEW", 8),
    ("8", "Where declarations must appear", "Declarations must appear on the principal display panel with the specified clear space around quantity declarations.", "DISPLAY_LOCATION", "MANUAL_REVIEW", 9),
    ("9", "Manner of declaration", "Declarations must be legible, prominent, contrasting and in Hindi or English; they must not need to be read through liquid and outer wrappers generally require declarations.", "VISUAL_DECLARATION", "MANUAL_REVIEW", 10),
    ("10", "Name and address", "Manufacturer, packer and importer names and complete addresses must be displayed, subject to the small-package provisions.", "ROLE_ADDRESS", "FAIL", 10),
    ("11", "General quantity declaration", "Net quantity excludes wrappers and packaging and must represent what the consumer receives; when-packed qualification is limited to Third Schedule commodities.", "QUANTITY_DECLARATION", "MANUAL_REVIEW", 11),
    ("12", "Manner of quantity declaration", "Quantity is declared by mass, length, area, volume or number as appropriate, subject to Fourth Schedule exceptions; misleading qualifiers are prohibited.", "QUANTITY_UNIT", "MANUAL_REVIEW", 12),
    ("13", "Units", "Use prescribed SI units and subunits; prohibited terms include dozen, score and gross; items sold by number use N or U.", "UNIT_FORMAT", "WARNING", 13),
    ("14", "Textile and similar goods", "Specified fabrics and similar goods require number and finished dimensions, with individual dimensions and prices where pieces differ.", "TEXTILE_DECLARATION", "MANUAL_REVIEW", 14),
    ("15", "Dimensions and weight", "Where dimensions or weight affect price, those details must be declared.", "DIMENSIONS", "MANUAL_REVIEW", 15),
    ("16", "Number of usable sheets", "Foil, tissues, waxed paper, toilet paper and similar sheet packages must state usable-sheet count and sheet dimensions.", "SHEET_DECLARATION", "MANUAL_REVIEW", 15),
    ("17", "Container type commodities", "Container-type commodities must declare number and relevant dimensions, diameter, depth or capacity.", "CONTAINER_DECLARATION", "MANUAL_REVIEW", 15),
    ("18", "Wholesale and retail dealer provisions", "Dealers cannot sell non-compliant packages or charge above MRP; alteration of MRP and dealer-side facts require inspection evidence.", "DEALER_CHECK", "MANUAL_REVIEW", 16),
    ("19", "Inspection and testing procedure", "Authorised officers may inspect premises, draw samples under the Fifth Schedule, test under the Sixth Schedule and record results under the Seventh Schedule.", "PHYSICAL_INSPECTION", "MANUAL_REVIEW", 17),
    ("20", "Seizure", "Non-compliant samples may be seized and action may follow under the Act.", "PHYSICAL_INSPECTION", "MANUAL_REVIEW", 19),
    ("21", "Premises testing", "Retail/wholesale premises testing is ordinarily avoided except for complaints, suspected tampering/leakage or missing declarations.", "PHYSICAL_INSPECTION", "MANUAL_REVIEW", 20),
    ("22", "Maximum permissible error", "Maximum permissible error is specified in the First Schedule and accounts for unavoidable variation and environmental conditions.", "MPE", "MANUAL_REVIEW", 21),
    ("23", "Deceptive packages", "A package giving an exaggerated or misleading impression of quantity may require repacking, relabeling, seizure or prosecution; image evidence alone cannot establish deception.", "DECEPTIVE_PACKAGE", "MANUAL_REVIEW", 22),
    ("24", "Wholesale packages", "Wholesale packages must declare identity/address, commodity identity and total retail-package count or net quantity.", "WHOLESALE_DECLARATION", "FAIL", 23),
    ("25", "Export packages", "Export packages cannot be sold in India unless repacked or relabeled under Chapter II.", "EXPORT_PACKAGE", "MANUAL_REVIEW", 23),
    ("26", "Exemptions", "Specified packages of 10 g/ml or less, restaurant fast food, specified drug formulations and agricultural produce above 50 kg are exempt subject to the PDF amendments.", "EXEMPTION", "NOT_APPLICABLE", 24),
    ("27", "Registration", "Manufacturers, packers and importers must register within 90 days; the PDF states the application and alteration fees.", "REGISTRATION", "MANUAL_REVIEW", 24),
    ("28", "Shorter address", "A shorter address may be separately registered if sufficient to identify the manufacturer or packer.", "REGISTRATION", "MANUAL_REVIEW", 25),
    ("29", "Public register", "The registering authority maintains a public register of manufacturers and packers.", "REGISTRATION", "MANUAL_REVIEW", 25),
    ("30", "State-wise lists", "State-wise lists of registered manufacturers and packers must be compiled and circulated.", "REGISTRATION", "MANUAL_REVIEW", 26),
    ("31", "Advertisements", "Advertisements mentioning retail sale price must also state net quantity or number, with the stated font-size relationship.", "ADVERTISEMENT", "MANUAL_REVIEW", 26),
]

CATEGORIES = {
    "BABY_FOOD": "Baby food", "WEANING_FOOD": "Weaning food", "BISCUITS": "Biscuits", "BREAD": "Bread",
    "BUTTER_MARGARINE": "Un-canned butter and margarine", "CEREALS_PULSES": "Cereals and pulses", "COFFEE": "Coffee",
    "TEA": "Tea", "BEVERAGE_MATERIALS": "Beverage materials", "EDIBLE_OIL": "Edible oils, vanaspati, ghee and butter oil",
    "MILK_POWDER": "Milk powder", "DETERGENT_POWDER": "Non-soapy detergent powder", "FLOUR": "Rice powder, flour, atta, rawa and suji",
    "SALT": "Salt", "LAUNDRY_SOAP": "Laundry soap", "DETERGENT_CAKE": "Non-soapy detergent cakes/bars", "TOILET_SOAP": "Toilet/bath soap",
    "SOFT_DRINK": "Aerated soft drinks/non-alcoholic beverages", "MINERAL_WATER": "Mineral/drinking water", "CEMENT": "Cement",
    "PAINT": "Paint, varnish and enamels", "PASTE_PAINT": "Paste and solid paint", "BASE_PAINT": "Base paint",
    "SHEET_COMMODITY": "Foil, tissues, waxed paper, toilet paper and similar sheets", "CONTAINER_COMMODITY": "Container-type commodity", "OTHER": "Other commodity",
}

PACKS = {
    "BABY_FOOD": [(100,"g"),(200,"g"),(300,"g"),(400,"g"),(500,"g"),(600,"g"),(700,"g"),(800,"g"),(900,"g"),(1,"kg"),(2,"kg"),(5,"kg"),(10,"kg")],
    "WEANING_FOOD": [(100,"g"),(200,"g"),(300,"g"),(400,"g"),(500,"g"),(600,"g"),(700,"g"),(800,"g"),(900,"g"),(1,"kg"),(2,"kg"),(5,"kg"),(10,"kg")],
    "BISCUITS": [(25,"g"),(50,"g"),(75,"g"),(100,"g"),(150,"g"),(200,"g"),(250,"g"),(300,"g")],
    "BREAD": [(100,"g")], "BUTTER_MARGARINE": [(25,"g"),(50,"g"),(100,"g"),(200,"g"),(500,"g"),(1,"kg"),(2,"kg"),(5,"kg")],
    "CEREALS_PULSES": [(100,"g"),(200,"g"),(500,"g"),(1,"kg"),(2,"kg"),(5,"kg")],
    "COFFEE": [(25,"g"),(50,"g"),(100,"g"),(200,"g"),(250,"g"),(500,"g"),(1,"kg")],
    "TEA": [(25,"g"),(50,"g"),(100,"g"),(125,"g"),(250,"g"),(500,"g"),(1,"kg")],
    "BEVERAGE_MATERIALS": [(25,"g"),(50,"g"),(100,"g"),(200,"g"),(500,"g"),(1,"kg")],
    "EDIBLE_OIL": [(50,"g"),(100,"g"),(200,"g"),(500,"g"),(1,"kg"),(2,"kg"),(3,"kg"),(5,"kg")],
    "MILK_POWDER": [(50,"g"),(100,"g"),(200,"g"),(500,"g"),(1,"kg")],
    "DETERGENT_POWDER": [(50,"g"),(100,"g"),(200,"g"),(500,"g"),(700,"g"),(1,"kg"),(1.5,"kg"),(2,"kg")],
    "FLOUR": [(100,"g"),(200,"g"),(500,"g"),(1,"kg"),(2,"kg"),(5,"kg")],
    "SALT": [(10,"g"),(50,"g"),(100,"g"),(200,"g"),(500,"g"),(750,"g"),(1,"kg"),(2,"kg"),(5,"kg")],
    "LAUNDRY_SOAP": [(50,"g"),(75,"g"),(100,"g")], "DETERGENT_CAKE": [(50,"g"),(75,"g"),(100,"g"),(125,"g"),(150,"g"),(200,"g"),(250,"g"),(300,"g")],
    "TOILET_SOAP": [(25,"g"),(50,"g"),(75,"g"),(100,"g"),(125,"g"),(150,"g")],
    "MINERAL_WATER": [(100,"ml"),(150,"ml"),(200,"ml"),(250,"ml"),(300,"ml"),(500,"ml"),(750,"ml"),(1,"l"),(1.5,"l"),(2,"l"),(3,"l"),(4,"l"),(5,"l")],
    "CEMENT": [(1,"kg"),(2,"kg"),(5,"kg"),(10,"kg"),(20,"kg"),(25,"kg"),(40,"kg"),(50,"kg")],
    "PAINT": [(50,"ml"),(100,"ml"),(200,"ml"),(500,"ml"),(1,"l"),(2,"l"),(3,"l"),(4,"l"),(5,"l")],
    "PASTE_PAINT": [(500,"g"),(1,"kg"),(1.5,"kg"),(2,"kg"),(3,"kg"),(5,"kg"),(7,"kg")],
    "BASE_PAINT": [(450,"ml"),(500,"ml"),(900,"ml"),(925,"ml"),(950,"ml"),(975,"ml"),(1,"l"),(3.6,"l"),(3.7,"l"),(3.8,"l"),(3.9,"l"),(4,"l")],
}

class Command(BaseCommand):
    help = "Seed rules and schedule data extracted from the supplied PDF."

    @transaction.atomic
    def handle(self, *args, **options):
        for code, name in CATEGORIES.items():
            CommodityCategory.objects.update_or_create(code=code, defaults={"name": name, "source_page": 29})
        for number, title, requirement, validation_type, severity, page in RULES:
            Rule.objects.update_or_create(rule_number=number, sub_rule="", defaults={"title": title, "requirement": requirement, "validation_type": validation_type, "severity": severity, "source_document": SOURCE, "source_page": str(page), "source_reference": f"Rule {number}"})
        for code, sizes in PACKS.items():
            category = CommodityCategory.objects.get(code=code)
            StandardPackSize.objects.filter(category=category).delete()
            StandardPackSize.objects.bulk_create([StandardPackSize(category=category, quantity_value=value, quantity_unit=unit, source_page=29) for value, unit in sizes])
        ScheduleEntry.objects.filter(schedule__in=["FIRST", "THIRD", "FOURTH"]).delete()
        mpe = [("Up to 50 g/ml", {"max": 50, "mpe": 9, "kind": "absolute"}), ("50–100 g/ml", {"max": 100, "mpe": 4.5, "kind": "percent"}), ("100–200 g/ml", {"max": 200, "mpe": 4.5, "kind": "absolute"}), ("200–300 g/ml", {"max": 300, "mpe": 9, "kind": "absolute"}), ("300–500 g/ml", {"max": 500, "mpe": 3, "kind": "percent"}), ("500–1000 g/ml", {"max": 1000, "mpe": 15, "kind": "absolute"}), ("1000–10000 g/ml", {"max": 10000, "mpe": 1.5, "kind": "percent"}), ("10000–15000 g/ml", {"max": 15000, "mpe": 150, "kind": "absolute"}), ("More than 15000 g/ml", {"max": None, "mpe": 1, "kind": "percent"})]
        ScheduleEntry.objects.bulk_create([ScheduleEntry(schedule="FIRST", commodity=label, data=data, source_page=28, source_reference="First Schedule") for label, data in mpe])
        for label, data in [("Length", {"up_to": 10, "mpe_percent": 2, "after_percent": 1}), ("Area", {"up_to": 10, "mpe_percent": 4, "after_percent": 1}), ("Number", {"mpe_percent": 2})]:
            ScheduleEntry.objects.create(schedule="FIRST", commodity=label, data=data, source_page=29, source_reference="First Schedule, Table II")
        for commodity in ["All kinds of soaps", "Lotions", "Cream, other than milk cream"]:
            ScheduleEntry.objects.create(schedule="THIRD", commodity=commodity, data={"when_packed": True}, source_page=32, source_reference="Third Schedule")
        fourth = {"Aerosol products":"weight", "Acids in liquid form":"weight_or_volume", "Compressed/liquefied gas excluding LPG":"weight_and_equivalent_volume", "Curd":"weight", "Electric cables":"length_or_weight", "Electric wire":"length_or_weight", "Fencing wire":"number_or_weight", "Fruits":"number_or_weight", "Furnace oil":"weight_or_volume", "Non-edible vegetable oil":"weight_or_volume", "Edible oil, vanaspati, ghee, butter oil":"weight_or_volume", "Heavy residual fuel oil":"weight", "Industrial diesel fuel":"volume", "Honey, malt extract, golden syrup, treacle":"weight", "Ice cream and similar frozen products":"volume", "Liquid chemicals":"weight_or_volume", "Liquefied petroleum gas":"weight", "Nails and wood screws":"number_or_weight", "Paints, varnish, varnish stains, enamels":"volume", "Paste paint and solid paint":"weight", "Rasgulla, gulabjamun and other sweet preparations":"weight", "Ready-made garments":"number", "Sauces":"weight", "Tyres and tubes":"number", "Yarn":"weight_or_length", "Cosmetics including creams, shampoo, lotions, perfumes":"weight_or_measure"}
        ScheduleEntry.objects.bulk_create([ScheduleEntry(schedule="FOURTH", commodity=commodity, data={"quantity_declaration": declaration}, source_page=33, source_reference="Fourth Schedule") for commodity, declaration in fourth.items()])
        Exemption.objects.update_or_create(code="SMALL_PACKAGE", defaults={"description":"Package of 10 g/ml or less.", "conditions":{"max_quantity":10}, "source_page":24})
        Exemption.objects.update_or_create(code="INDUSTRIAL_CONSUMER", defaults={"description":"Package intended for an industrial consumer.", "conditions":{"consumer_type":"INDUSTRIAL"}, "source_page":4})
        Exemption.objects.update_or_create(code="INSTITUTIONAL_CONSUMER", defaults={"description":"Package intended for an institutional consumer.", "conditions":{"consumer_type":"INSTITUTIONAL"}, "source_page":4})
        self.stdout.write(self.style.SUCCESS(f"Seeded {Rule.objects.count()} rules, {StandardPackSize.objects.count()} standard sizes and schedule data from {SOURCE}."))
