# ruff: noqa: E501

from typing import TypedDict

from app.util.misc import flatten_list


class PartnerOrganization(TypedDict):
    products: list[str]
    organisatie_naam: str
    description: str  # Markdown description
    description_short: str  # Short summary (max 120 characters)


partner_organizations: list[PartnerOrganization] = [
    {
        "organisatie_naam": "Caching",
        "description": (
            "**Caching – Ondersteuning op maat voor ondernemers**\n"
            "\n"
            "Caching helpt ondernemers. Ons doel is het helpen van startups en bestaande bedrijven te groeien naar succesvolle ondernemingen."
            "Hoewel wij ondernemers in elke sector ondersteunen, hebben we een sterke affiniteit met de creatieve sector."
            "We zijn bekend met de aspecten van het ondernemerschap waar veel creatievelingen tegenaan lopen. "
            "Met onze persoonlijke en toegankelijke aanpak helpen we je om jouw onderneming verder te laten groeien.\n"
            "\n"
            "- **Versterken van jouw onderneming**: advies en begeleiding bij het optimaliseren van bedrijfsprocessen.\n"
            "- **Ondersteuning bij administratie en financiële vraagstukken**: ordenen en opstellen van administratie en financiële overzichten.\n"
            "- **Coaching en begeleiding op maat**: ieder traject aangepast aan de specifieke hulpvraag en ervaring van de ondernemer."
        ),
        "description_short": "Ondersteuning en coaching voor ondernemers, met speciale affiniteit voor de creatieve sector.",
        "products": ["1.1", "1.2", "1.3", "1.4", "1.6"],
    },
    {
        "organisatie_naam": "Content Kitchen",
        "description": (
            "Content Kitchen is een bureau voor trendprognose, merkanalyse en contentstrategie. "
            "We helpen ondernemers met het (re)positioneren van hun merk. Dankzij onze jarenlange ervaring bieden we een frisse blik en persoonlijk advies. "
            "Het traject omvat: intakegesprek, quick-scan van huidige merk- & contentstrategie en een Pressure Cooker sessie voor campagneplanning."
        ),
        "description_short": "Bureau voor trendprognose, merkanalyse en contentstrategie met persoonlijk advies voor merkpositionering.",
        "products": ["1.4"],
    },
    {
        "organisatie_naam": "Cultuur+Ondernemen",
        "description": (
            "Cultuur+Ondernemen is hét kenniscentrum voor ondernemerschap in de culturele en creatieve sector en financier voor cultureel ondernemers. "
            "Wij versterken culturele organisaties en zelfstandig werkende kunstenaars door advies op maat en digitale kennisgidsen via ons platform."
        ),
        "description_short": "Kenniscentrum voor ondernemerschap in de culturele en creatieve sector met advies en kennisgidsen.",
        "products": ["1.1", "1.2", "1.3"],
    },
    {
        "organisatie_naam": "DDK",
        "description": (
            "DDK is een communicatie- en marketingbureau in Utrecht. We helpen ondernemers bij wervende (online)campagnes, branding en merkverhalen, altijd gebaseerd op grondige doelgroepanalyse."
        ),
        "description_short": "Communicatie- en marketingbureau voor wervende campagnes, branding en merkverhalen in Utrecht.",
        "products": ["1.1", "1.2", "1.3", "1.4", "1.6"],
    },
    {
        "organisatie_naam": "Geldfit Zakelijk",
        "description": (
            "Team Ondernemersadvies Geldfit biedt QuickScans voor financiële gezondheid, rapporten met duurzaam advies en begeleiding bij (door)start- en investeringsplannen."
        ),
        "description_short": "QuickScans voor financiële gezondheid met duurzaam advies en begeleiding bij investeringsplannen.",
        "products": ["1.1", "1.3"],
    },
    {
        "organisatie_naam": "GetOn",
        "description": (
            "GetOn helpt ondernemers met websites, social media en AI-tools. Met praktische cursussen zoals SEO, conversieoptimalisatie en storytelling professionaliseer je je online aanwezigheid."
        ),
        "description_short": "Hulp voor ondernemers met websites, social media en AI-tools via praktische cursussen.",
        "products": ["1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "4.1", "4.2", "4.3"],
    },
    {
        "organisatie_naam": "Hogenkamp Agrarische Coaching",
        "description": (
            "Specialistische coaching voor agrariërs bij persoonlijke ontwikkeling, keuzestress en transitie naar baan in loondienst met affiniteit voor de agrarische sector."
        ),
        "description_short": "Specialistische coaching voor agrariërs bij persoonlijke ontwikkeling en carrièretransitie.",
        "products": ["1.1", "1.2", "1.3", "1.4"],
    },
    {
        "organisatie_naam": "IMK - Het Instituut voor het Midden- en Kleinbedrijf",
        "description": (
            "IMK ondersteunt zzp'ers en MKB in alle fases van hun onderneming met maatwerk coaching, van opstart en groei tot doorstart- en beëindigingsplannen."
        ),
        "description_short": "Maatwerk coaching voor zzp'ers en MKB in alle ondernemingsfases van opstart tot beëindiging.",
        "products": ["1.1", "1.2", "1.3", "1.4", "3.7", "3.8", "3.9"],
    },
    {
        "organisatie_naam": "Lockefeer Innovatie & Realisatie",
        "description": (
            "Strategische begeleiding in 5 sessies om kansen en risico's in kaart te brengen, Design Thinking methodieken toe te passen en een concreet actieplan te valideren en te starten."
        ),
        "description_short": "Strategische begeleiding met Design Thinking methodieken voor concrete actieplanning.",
        "products": ["1.1", "1.2", "1.3", "1.4"],
    },
    {
        "organisatie_naam": "Maakt Ondernemers Beter (MOB)",
        "description": (
            "Pragmatische coaching door ervaren ondernemerscoaches, gericht op bedrijfskundige vraagstukken, cashflowprognoses, salesplannen en verduurzaming."
        ),
        "description_short": "Pragmatische coaching voor bedrijfskundige vraagstukken, cashflow en salesplannen.",
        "products": ["1.1", "1.2", "1.3", "1.4", "3.6", "3.7"],
    },
    {
        "organisatie_naam": "Over Rood",
        "description": (
            "Vrijwillige trajectmanagers begeleiden ondernemers met schulden, administratie, BBZ-aanvragen en stoppers bij bedrijf. Van intake tot afwikkeling en arbeidsbemiddeling."
        ),
        "description_short": "Begeleiding voor ondernemers met schulden, administratie en BBZ-aanvragen tot arbeidsbemiddeling.",
        "products": [
            "1.1",
            "1.2",
            "1.3",
            "1.4",
            "1.5",
            "1.6",
            "1.7",
            "1.8",
            "1.9",
            "3.1",
            "3.2",
            "3.3",
            "3.4",
            "3.5",
            "3.6",
            "3.7",
            "3.8",
        ],
    },
    {
        "organisatie_naam": "Power by Peers",
        "description": (
            "Peer-to-peer methodiek voor zzp'ers met ondernemersscans, online diensten zoals websitemanagement, rollenspellen en liquiditeitsbegrotingen."
        ),
        "description_short": "Peer-to-peer methodiek voor zzp'ers met ondernemersscans en online diensten.",
        "products": ["1.1", "1.2", "1.3", "1.4", "1.7", "1.8", "4.2", "Toekomstgesprek"],
    },
    {
        "organisatie_naam": "Solvid Ondernemen",
        "description": (
            "Coaching en sparring voor startende ondernemers, met digitale tools voor liquiditeitsbegrotingen en marketingadvies, meestal in 3 sessies."
        ),
        "description_short": "Coaching voor startende ondernemers met digitale tools en marketingadvies in 3 sessies.",
        "products": [
            "1.1",
            "1.2",
            "1.3",
            "1.4",
            "1.5",
            "1.6",
            "1.7",
            "1.8",
            "3.1",
            "3.2",
            "3.6",
            "3.7",
            "3.8",
            "4.1",
            "4.2",
            "Toekomstgesprek",
        ],
    },
    {
        "organisatie_naam": "Stevelink Bedrijfsadvies",
        "description": (
            "Advisering voor omzetgroei, kostenoptimalisatie en margeverbetering door analyse van strategie, verdienmodellen en branche-specifieke expertise."
        ),
        "description_short": "Advisering voor omzetgroei, kostenoptimalisatie en margeverbetering met branche-expertise.",
        "products": ["1.1", "1.2", "1.3", "1.4", "Toekomstgesprek"],
    },
    {
        "organisatie_naam": "Stichting Ondernemersklankbord (OKB)",
        "description": (
            "Gratis klankbordtrajecten van zes maanden met ervaren adviseurs, volledig op maat en gericht op preventief handelen en faillissements­ voorkoming."
        ),
        "description_short": "Gratis klankbordtrajecten van zes maanden voor preventief handelen en faillissementsvoorkoming.",
        "products": ["2.1", "Toekomstgesprek"],
    },
    {
        "organisatie_naam": "Certa Advocaten",
        "description": (
            "Advies en bijstand in arbeidsrecht, ondernemingsrecht, faillissementsrecht, incasso, vastgoed- en bestuursrecht, met digitale werkwijze."
        ),
        "description_short": "Advies in arbeids-, ondernemings-, faillissements-, vastgoed- en bestuursrecht met digitale werkwijze.",
        "products": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "2.10"],
    },
    {
        "organisatie_naam": "Okkerse & Schop Advocaten",
        "description": (
            "Praktisch en oplossingsgericht advocatenkantoor met expertise in ondernemingsrecht, schuldhulpverlening, ICT-recht, privacy en meer, met vaste contactpersoon."
        ),
        "description_short": "Praktisch advocatenkantoor voor ondernemings-, ICT-recht en schuldhulpverlening met vaste contactpersoon.",
        "products": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "2.10"],
    },
    {
        "organisatie_naam": "Sociaal Raadslieden U-centraal",
        "description": (
            "Ondersteuning bij sociaal-juridische vragen rondom sociale zekerheid, financiën, wonen, vreemdelingenrecht en doorverwijzing naar buurtteams."
        ),
        "description_short": "Ondersteuning bij sociaal-juridische vragen over sociale zekerheid, financiën en wonen.",
        "products": [],
    },
    {
        "organisatie_naam": "DOK030",
        "description": (
            "Hulp bij administratie, Bbz-aanvragen en algemeen financieel inzicht voor ondernemers in Utrecht."
        ),
        "description_short": "Hulp bij administratie, BBZ-aanvragen en financieel inzicht voor ondernemers in Utrecht.",
        "products": ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9"],
    },
    {
        "organisatie_naam": "The Bookie",
        "description": (
            "Boekhouding, btw- en inkomstenbelastingaangiftes, jaarcijfers, prognoses en advisering met boekhouders, accountants en juristen in Utrecht."
        ),
        "description_short": "Boekhouding, belastingaangiftes en financiële advisering met professionals in Utrecht.",
        "products": ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9"],
    },
    {
        "organisatie_naam": "Circulair ondernemen",
        "description": (
            "Netwerken zoals RVO, Cirkelregio Utrecht en CIRCO Hub Midden Nederland voor advies over circulair ontwerpen, hergebruik en afvalvermindering."
        ),
        "description_short": "Netwerken voor advies over circulair ontwerpen, hergebruik en afvalvermindering.",
        "products": [],
    },
    {
        "organisatie_naam": "Energieloket",
        "description": (
            "Gratis advies via de gemeente Utrecht voor subsidies, energie-efficiëntie, netcongestie, duurzame mobiliteit en financieringsmogelijkheden."
        ),
        "description_short": "Gratis advies van gemeente Utrecht voor subsidies, energie-efficiëntie en duurzame mobiliteit.",
        "products": [],
    },
    {
        "organisatie_naam": "Impact030",
        "description": (
            "Netwerk en advies voor impactondernemers, monitoring via Utrechtse Nieuwe Economie Index en events om samenwerking te versterken."
        ),
        "description_short": "Netwerk en advies voor impactondernemers met monitoring en events voor samenwerking.",
        "products": [],
    },
    {
        "organisatie_naam": "Werkcentrum ‘Midden-Utrecht’",
        "description": (
            "Loopbaanadvies, begeleiding, (om)scholing en praktijkleren mbo voor ondernemers en werkzoekenden in de regio Midden-Utrecht."
        ),
        "description_short": "Loopbaanadvies, begeleiding en (om)scholing voor ondernemers en werkzoekenden in Midden-Utrecht.",
        "products": [],
    },
    {
        "organisatie_naam": "Kade 2",
        "description": "",
        "description_short": "",
        "products": ["Toekomstgesprek"],
    },
    {
        "organisatie_naam": "Zuidweg & Partners",
        "description": "",
        "description_short": "",
        "products": ["SHVO intake"],
    },
    {
        "organisatie_naam": "Instituut voor het Midden- en Kleinbedrijf",
        "description": "",
        "description_short": "",
        "products": ["Toekomstgesprek"],
    },
]


required_products: list[str] = flatten_list([o["products"] for o in partner_organizations])
