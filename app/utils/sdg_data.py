"""
SDG Targets data module
Contains the targets for each Sustainable Development Goal (SDG)
"""

# Dictionary mapping SDG numbers to their metadata (name, color, icon)
SDG_INFO = {
    1:  {'name': 'No Poverty',                 'color_code': '#E5243B', 'icon': 'fa-hand-holding-usd'},
    2:  {'name': 'Zero Hunger',                'color_code': '#DDA63A', 'icon': 'fa-seedling'},
    3:  {'name': 'Good Health & Well-being',   'color_code': '#4C9F38', 'icon': 'fa-heartbeat'},
    4:  {'name': 'Quality Education',          'color_code': '#C5192D', 'icon': 'fa-graduation-cap'},
    5:  {'name': 'Gender Equality',            'color_code': '#FF3A21', 'icon': 'fa-venus-mars'},
    6:  {'name': 'Clean Water & Sanitation',   'color_code': '#26BDE2', 'icon': 'fa-tint'},
    7:  {'name': 'Affordable & Clean Energy',  'color_code': '#FCC30B', 'icon': 'fa-bolt'},
    8:  {'name': 'Decent Work & Economic Growth', 'color_code': '#A21942', 'icon': 'fa-briefcase'},
    9:  {'name': 'Industry, Innovation & Infrastructure', 'color_code': '#FD6925', 'icon': 'fa-industry'},
    10: {'name': 'Reduced Inequalities',       'color_code': '#DD1367', 'icon': 'fa-arrows-alt-h'},
    11: {'name': 'Sustainable Cities & Communities', 'color_code': '#FD9D24', 'icon': 'fa-city'},
    12: {'name': 'Responsible Consumption & Production', 'color_code': '#BF8B2E', 'icon': 'fa-recycle'},
    13: {'name': 'Climate Action',             'color_code': '#3F7E44', 'icon': 'fa-cloud-sun-rain'},
    14: {'name': 'Life Below Water',           'color_code': '#0A97D9', 'icon': 'fa-water'},
    15: {'name': 'Life on Land',               'color_code': '#56C02B', 'icon': 'fa-tree'},
    16: {'name': 'Peace, Justice & Strong Institutions', 'color_code': '#00689D', 'icon': 'fa-landmark'},
    17: {'name': 'Partnerships for the Goals', 'color_code': '#19486A', 'icon': 'fa-handshake'}
}

# Dictionary mapping SDG numbers to their targets
SDG_TARGETS = {
    1: [
        "1.1 By 2030, eradicate extreme poverty for all people everywhere",
        "1.2 By 2030, reduce at least by half the proportion of men, women and children living in poverty",
        "1.3 Implement social protection systems for all",
        "1.4 By 2030, ensure equal rights to economic resources",
        "1.5 By 2030, build the resilience of the poor and vulnerable"
    ],
    2: [
        "2.1 By 2030, end hunger and ensure access to safe, nutritious food",
        "2.2 By 2030, end all forms of malnutrition",
        "2.3 By 2030, double the agricultural productivity and incomes of small-scale food producers",
        "2.4 By 2030, ensure sustainable food production systems",
        "2.5 By 2020, maintain the genetic diversity of seeds, plants and animals"
    ],
    3: [
        "3.1 By 2030, reduce the global maternal mortality ratio",
        "3.2 By 2030, end preventable deaths of newborns and children under 5",
        "3.3 By 2030, end the epidemics of AIDS, tuberculosis, malaria and other diseases",
        "3.4 By 2030, reduce premature mortality from non-communicable diseases",
        "3.5 Strengthen the prevention and treatment of substance abuse"
    ],
    4: [
        "4.1 By 2030, ensure all girls and boys complete free, equitable and quality education",
        "4.2 By 2030, ensure all girls and boys have access to quality early childhood development",
        "4.3 By 2030, ensure equal access for all women and men to affordable education",
        "4.4 By 2030, increase the number of youth and adults with relevant skills for employment",
        "4.5 By 2030, eliminate gender disparities in education"
    ],
    5: [
        "5.1 End all forms of discrimination against all women and girls everywhere",
        "5.2 Eliminate all forms of violence against all women and girls",
        "5.3 Eliminate all harmful practices, such as child marriage",
        "5.4 Recognize and value unpaid care and domestic work",
        "5.5 Ensure women's full and effective participation and equal opportunities for leadership"
    ],
    6: [
        "6.1 By 2030, achieve universal and equitable access to safe and affordable drinking water",
        "6.2 By 2030, achieve access to adequate and equitable sanitation and hygiene for all",
        "6.3 By 2030, improve water quality by reducing pollution",
        "6.4 By 2030, substantially increase water-use efficiency across all sectors",
        "6.5 By 2030, implement integrated water resources management"
    ],
    7: [
        "7.1 By 2030, ensure universal access to affordable, reliable and modern energy services",
        "7.2 By 2030, increase substantially the share of renewable energy in the global energy mix",
        "7.3 By 2030, double the global rate of improvement in energy efficiency",
        "7.a By 2030, enhance international cooperation to facilitate access to clean energy",
        "7.b By 2030, expand infrastructure and upgrade technology for modern energy services"
    ],
    8: [
        "8.1 Sustain per capita economic growth in accordance with national circumstances",
        "8.2 Achieve higher levels of economic productivity through diversification",
        "8.3 Promote development-oriented policies that support productive activities",
        "8.4 Improve global resource efficiency in consumption and production",
        "8.5 By 2030, achieve full and productive employment and decent work for all"
    ],
    9: [
        "9.1 Develop quality, reliable, sustainable and resilient infrastructure",
        "9.2 Promote inclusive and sustainable industrialization",
        "9.3 Increase the access of small-scale enterprises to financial services",
        "9.4 By 2030, upgrade infrastructure and retrofit industries to make them sustainable",
        "9.5 Enhance scientific research, upgrade technological capabilities"
    ],
    10: [
        "10.1 By 2030, progressively achieve and sustain income growth of the bottom 40%",
        "10.2 By 2030, empower and promote the social, economic and political inclusion of all",
        "10.3 Ensure equal opportunity and reduce inequalities of outcome",
        "10.4 Adopt policies, especially fiscal, wage and social protection policies",
        "10.5 Improve the regulation and monitoring of global financial markets"
    ],
    11: [
        "11.1 By 2030, ensure access for all to adequate, safe and affordable housing",
        "11.2 By 2030, provide access to safe, affordable, accessible and sustainable transport",
        "11.3 By 2030, enhance inclusive and sustainable urbanization",
        "11.4 Strengthen efforts to protect and safeguard the world's cultural and natural heritage",
        "11.5 By 2030, significantly reduce the number of deaths caused by disasters"
    ],
    12: [
        "12.1 Implement the 10-Year Framework of Programmes on Sustainable Consumption and Production",
        "12.2 By 2030, achieve the sustainable management and efficient use of natural resources",
        "12.3 By 2030, halve per capita global food waste at the retail and consumer levels",
        "12.4 By 2020, achieve the environmentally sound management of chemicals and all wastes",
        "12.5 By 2030, substantially reduce waste generation through prevention, reduction, recycling"
    ],
    13: [
        "13.1 Strengthen resilience and adaptive capacity to climate-related hazards",
        "13.2 Integrate climate change measures into national policies, strategies and planning",
        "13.3 Improve education, awareness-raising on climate change mitigation and adaptation",
        "13.a Implement the commitment to the Green Climate Fund",
        "13.b Promote mechanisms for raising capacity for climate planning and management"
    ],
    14: [
        "14.1 By 2025, prevent and significantly reduce marine pollution of all kinds",
        "14.2 By 2020, sustainably manage and protect marine and coastal ecosystems",
        "14.3 Minimize and address the impacts of ocean acidification",
        "14.4 By 2020, effectively regulate harvesting and end overfishing",
        "14.5 By 2020, conserve at least 10% of coastal and marine areas"
    ],
    15: [
        "15.1 By 2020, ensure the conservation, restoration and sustainable use of terrestrial ecosystems",
        "15.2 By 2020, promote the implementation of sustainable management of all types of forests",
        "15.3 By 2030, combat desertification, restore degraded land and soil",
        "15.4 By 2030, ensure the conservation of mountain ecosystems",
        "15.5 Take urgent and significant action to reduce the degradation of natural habitats"
    ],
    16: [
        "16.1 Significantly reduce all forms of violence and related death rates everywhere",
        "16.2 End abuse, exploitation, trafficking and all forms of violence against children",
        "16.3 Promote the rule of law at the national and international levels",
        "16.4 By 2030, significantly reduce illicit financial and arms flows",
        "16.5 Substantially reduce corruption and bribery in all their forms"
    ],
    17: [
        "17.1 Strengthen domestic resource mobilization to improve domestic capacity for tax collection",
        "17.2 Developed countries to implement fully their official development assistance commitments",
        "17.3 Mobilize additional financial resources for developing countries",
        "17.4 Assist developing countries in attaining long-term debt sustainability",
        "17.5 Adopt and implement investment promotion regimes for least developed countries"
    ]
}
