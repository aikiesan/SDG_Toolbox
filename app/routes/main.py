from flask import Blueprint, render_template, jsonify, current_app, request, abort
import os
import sqlite3
from app import db
from sqlalchemy import inspect, text
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command

main_bp = Blueprint('main', __name__)

@main_bp.route('/debug/database')
def debug_database():
    db_path = os.path.join(current_app.instance_path, 'sdgassessmentdev.db')
    results = {'database_path': db_path, 'exists': os.path.exists(db_path)}
    
    if not os.path.exists(db_path):
        return jsonify(results)
    
    conn = sqlite3.connect(db_path)
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    results['tables'] = [t[0] for t in tables]
    
    if 'sdg_questions' in results['tables']:
        columns = conn.execute("PRAGMA table_info(sdg_questions)").fetchall()
        results['sdg_questions_columns'] = [c[1] for c in columns]
    
    conn.close()
    return jsonify(results)

@main_bp.route('/debug/db')
def debug_db():
    from app.utils.db import get_fresh_db
    conn = get_fresh_db()
    users_columns = [col[1] for col in conn.execute("PRAGMA table_info(users)").fetchall()]
    conn.close()
    return jsonify({"users_table_columns": users_columns})

@main_bp.route('/sdg-information-hub')
def sdg_information_hub():
    """Display information about SDGs."""
    # --- FULL SDG SUMMARIES ---
    sdg_summaries = {
        1: "End poverty in all its forms everywhere. In the context of architecture, this involves creating affordable housing solutions, designing inclusive public spaces, and planning infrastructure that enables economic opportunities.",
        2: "End hunger, achieve food security and improved nutrition and promote sustainable agriculture. Architects can contribute through urban farming facilities, community gardens, and designing food production and distribution systems.",
        3: "Ensure healthy lives and promote well-being for all at all ages. This includes designing buildings with proper ventilation, natural light, and green spaces that promote physical and mental health.",
        4: "Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all. Architectural contributions include designing accessible, safe, and inspiring learning environments that serve diverse communities.",
        5: "Achieve gender equality and empower all women and girls. In architecture, this means creating safe public spaces, gender-inclusive facilities, and environments that support women's economic participation.",
        6: "Ensure availability and sustainable management of water and sanitation for all. Architectural strategies include water-saving building systems, rainwater harvesting, and sustainable urban drainage solutions.",
        7: "Ensure access to affordable, reliable, sustainable and modern energy for all. This involves designing energy-efficient buildings, integrating renewable energy systems, and creating smart energy distribution networks.",
        8: "Promote sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all. Architects can contribute through flexible workspaces, local job-creating projects, and inclusive economic infrastructure.",
        9: "Build resilient infrastructure, promote inclusive and sustainable industrialization and foster innovation. This includes designing durable, adaptable structures using sustainable materials and innovative construction technologies.",
        10: "Reduce inequality within and among countries. Architectural approaches include equitable public space design, accessible housing for all income levels, and inclusive community facilities.",
        11: "Make cities and human settlements inclusive, safe, resilient and sustainable. This is central to architecture through sustainable urban planning, resilient building design, and creating healthy, accessible urban environments.",
        12: "Ensure sustainable consumption and production patterns. For architecture, this means using sustainable materials, designing for minimal waste, and creating circular building lifecycles.",
        13: "Take urgent action to combat climate change and its impacts. Architectural responses include designing low-carbon buildings, climate-adaptive structures, and sustainable urban environments that mitigate climate impacts.",
        14: "Conserve and sustainably use the oceans, seas and marine resources for sustainable development. This includes designing coastal infrastructure that protects marine ecosystems and buildings that reduce water pollution.",
        15: "Protect, restore and promote sustainable use of terrestrial ecosystems. Architectural approaches include biodiversity-supporting design, sustainable land use, and integration of natural ecosystems into built environments.",
        16: "Promote peaceful and inclusive societies for sustainable development. In architectural terms, this means creating safe community spaces, designing for social cohesion, and supporting transparent institutions.",
        17: "Strengthen the means of implementation and revitalize the global partnership for sustainable development. Architects can contribute through international knowledge sharing and collaborative design approaches."
    }

    # --- FULL SDG TARGETS ---
    sdg_targets = {
        1: [
            {"code": "1.1", "text": "By 2030, eradicate extreme poverty for all people everywhere"},
            {"code": "1.2", "text": "By 2030, reduce at least by half the proportion of people living in poverty"},
            {"code": "1.4", "text": "By 2030, ensure that all men and women, in particular the poor and the vulnerable, have equal rights to economic resources, as well as access to basic services"}
        ],
        2: [
            {"code": "2.1", "text": "By 2030, end hunger and ensure access by all people to safe, nutritious and sufficient food"},
            {"code": "2.3", "text": "By 2030, double the agricultural productivity and incomes of small-scale food producers"},
            {"code": "2.4", "text": "By 2030, ensure sustainable food production systems and implement resilient agricultural practices"}
        ],
        3: [
            {"code": "3.4", "text": "By 2030, reduce by one third premature mortality from non-communicable diseases"},
            {"code": "3.9", "text": "By 2030, substantially reduce the number of deaths and illnesses from hazardous chemicals and air, water and soil pollution and contamination"}
        ],
        4: [
            {"code": "4.1", "text": "By 2030, ensure that all girls and boys complete free, equitable and quality primary and secondary education"},
            {"code": "4.a", "text": "Build and upgrade education facilities that are child, disability and gender sensitive and provide safe, non-violent, inclusive and effective learning environments for all"}
        ],
        5: [
            {"code": "5.1", "text": "End all forms of discrimination against all women and girls everywhere"},
            {"code": "5.5", "text": "Ensure women's full and effective participation and equal opportunities for leadership at all levels of decision-making"}
        ],
        6: [
            {"code": "6.1", "text": "By 2030, achieve universal and equitable access to safe and affordable drinking water for all"},
            {"code": "6.3", "text": "By 2030, improve water quality by reducing pollution, eliminating dumping and minimizing release of hazardous chemicals and materials"}
        ],
        7: [
            {"code": "7.1", "text": "By 2030, ensure universal access to affordable, reliable and modern energy services"},
            {"code": "7.2", "text": "By 2030, increase substantially the share of renewable energy in the global energy mix"}
        ],
        8: [
            {"code": "8.4", "text": "Improve progressively, through 2030, global resource efficiency in consumption and production and endeavour to decouple economic growth from environmental degradation"},
            {"code": "8.5", "text": "By 2030, achieve full and productive employment and decent work for all women and men, including for young people and persons with disabilities"}
        ],
        9: [
            {"code": "9.1", "text": "Develop quality, reliable, sustainable and resilient infrastructure to support economic development and human well-being"},
            {"code": "9.4", "text": "By 2030, upgrade infrastructure and retrofit industries to make them sustainable, with increased resource-use efficiency"}
        ],
        10: [
            {"code": "10.2", "text": "By 2030, empower and promote the social, economic and political inclusion of all, irrespective of age, sex, disability, race, ethnicity, origin, religion or economic or other status"},
            {"code": "10.3", "text": "Ensure equal opportunity and reduce inequalities of outcome, including by eliminating discriminatory laws, policies and practices"}
        ],
        11: [
            {"code": "11.1", "text": "By 2030, ensure access for all to adequate, safe and affordable housing and basic services and upgrade slums"},
            {"code": "11.3", "text": "By 2030, enhance inclusive and sustainable urbanization and capacity for participatory, integrated and sustainable human settlement planning"},
            {"code": "11.7", "text": "By 2030, provide universal access to safe, inclusive and accessible, green and public spaces, in particular for women and children, older persons and persons with disabilities"}
        ],
        12: [
            {"code": "12.2", "text": "By 2030, achieve the sustainable management and efficient use of natural resources"},
            {"code": "12.5", "text": "By 2030, substantially reduce waste generation through prevention, reduction, recycling and reuse"}
        ],
        13: [
            {"code": "13.1", "text": "Strengthen resilience and adaptive capacity to climate-related hazards and natural disasters in all countries"},
            {"code": "13.2", "text": "Integrate climate change measures into national policies, strategies and planning"}
        ],
        14: [
            {"code": "14.1", "text": "By 2025, prevent and significantly reduce marine pollution of all kinds"},
            {"code": "14.2", "text": "By 2020, sustainably manage and protect marine and coastal ecosystems to avoid significant adverse impacts"}
        ],
        15: [
            {"code": "15.1", "text": "By 2020, ensure the conservation, restoration and sustainable use of terrestrial and inland freshwater ecosystems"},
            {"code": "15.2", "text": "By 2020, promote the implementation of sustainable management of all types of forests"}
        ],
        16: [
            {"code": "16.1", "text": "Significantly reduce all forms of violence and related death rates everywhere"},
            {"code": "16.7", "text": "Ensure responsive, inclusive, participatory and representative decision-making at all levels"}
        ],
        17: [
            {"code": "17.16", "text": "Enhance the global partnership for sustainable development, complemented by multi-stakeholder partnerships"},
            {"code": "17.17", "text": "Encourage and promote effective public, public-private and civil society partnerships"}
        ]
    }

    # --- FULL SDG APPLICATIONS ---
    sdg_applications = {
        1: [
            "Design affordable housing that reduces construction and operating costs while maintaining quality",
            "Create mixed-income developments to prevent segregation based on economic status",
            "Implement passive design strategies to reduce energy costs for occupants"
        ],
        2: [
            "Design community gardens and urban agriculture facilities in building designs",
            "Create markets and food distribution infrastructure in underserved areas",
            "Design food-producing landscaping and edible architecture"
        ],
        3: [
            "Use biophilic design principles to connect occupants with nature",
            "Prioritize natural ventilation and indoor air quality in buildings",
            "Design active spaces that encourage movement and physical activity"
        ],
        4: [
            "Design flexible learning spaces that accommodate diverse teaching methods",
            "Create safe and accessible educational facilities for all users",
            "Implement design elements that stimulate learning and creativity"
        ],
        5: [
            "Design public spaces with adequate lighting and visibility to ensure safety for women",
            "Create equitable facilities with consideration for gender-specific needs",
            "Design community spaces that facilitate women's economic participation"
        ],
        6: [
            "Implement rainwater harvesting and greywater reuse systems",
            "Design water-efficient buildings with low-flow fixtures",
            "Create sustainable urban drainage systems (SUDS)"
        ],
        7: [
            "Integrate renewable energy systems into building design",
            "Optimize building orientation and envelope for energy efficiency",
            "Design district heating and cooling systems for greater efficiency"
        ],
        8: [
            "Design flexible workspaces that support diverse economic activities",
            "Use local materials and labor to support regional economies",
            "Create multipurpose spaces that maximize economic return on investment"
        ],
        9: [
            "Design buildings using innovative construction technologies",
            "Create adaptable structures that can change with evolving needs",
            "Integrate smart building systems for improved efficiency and function"
        ],
        10: [
            "Design accessible buildings that accommodate users of all abilities",
            "Create inclusive public spaces that welcome diverse communities",
            "Design housing for multiple income levels within the same development"
        ],
        11: [
            "Implement sustainable urban design principles for entire communities",
            "Design resilient buildings that can withstand climate events",
            "Create walkable neighborhoods with mixed-use development"
        ],
        12: [
            "Design buildings with reused or recycled materials",
            "Plan for building disassembly and material reuse at end of life",
            "Reduce construction waste through precise design and prefabrication"
        ],
        13: [
            "Design buildings that minimize carbon emissions across their lifecycle",
            "Create structures that can adapt to changing climate conditions",
            "Implement green infrastructure to reduce urban heat island effect"
        ],
        14: [
            "Design coastal buildings to minimize impact on marine ecosystems",
            "Create infrastructure that prevents runoff pollution into waterways",
            "Develop floating architecture that respects marine environments"
        ],
        15: [
            "Design green roofs and walls to support biodiversity",
            "Integrate existing ecosystems into building sites with minimal disruption",
            "Use sustainable forestry products in construction"
        ],
        16: [
            "Design community spaces that facilitate dialogue and cooperation",
            "Create safe environments through crime prevention through environmental design",
            "Design transparent and accessible government and institutional buildings"
        ],
        17: [
            "Participate in international design collaborations and knowledge sharing",
            "Implement globally successful sustainable building strategies locally",
            "Design demonstration projects that promote sustainability partnerships"
        ]
    }

    # --- FULL SDG RESOURCES ---
    sdg_resources = {
        1: [
            {"title": "UN SDG 1 - No Poverty", "url": "https://sdgs.un.org/goals/goal1", "icon": "globe", "source": "United Nations"},
            {"title": "Architecture for Humanity: Design Like You Give a Damn", "url": "https://www.architectureforhumanity.org", "icon": "book", "source": "Architecture for Humanity"}
        ],
        2: [
            {"title": "UN SDG 2 - Zero Hunger", "url": "https://sdgs.un.org/goals/goal2", "icon": "globe", "source": "United Nations"},
            {"title": "Urban Agriculture Integration Toolkit", "url": "https://www.urbanfarmingplanet.org", "icon": "file-text", "source": "Urban Farming Institute"}
        ],
        3: [
            {"title": "UN SDG 3 - Good Health and Well-being", "url": "https://sdgs.un.org/goals/goal3", "icon": "globe", "source": "United Nations"},
            {"title": "WELL Building Standard", "url": "https://www.wellcertified.com", "icon": "award", "source": "International WELL Building Institute"}
        ],
        4: [
            {"title": "UN SDG 4 - Quality Education", "url": "https://sdgs.un.org/goals/goal4", "icon": "globe", "source": "United Nations"},
            {"title": "Designing Quality Learning Spaces", "url": "https://www.education.govt.nz/school/property-and-transport/projects-and-design/design/designing-quality-learning-spaces/", "icon": "book", "source": "Ministry of Education"}
        ],
        5: [
            {"title": "UN SDG 5 - Gender Equality", "url": "https://sdgs.un.org/goals/goal5", "icon": "globe", "source": "United Nations"},
            {"title": "Gender-Responsive Urban Planning and Design", "url": "https://unhabitat.org/sites/default/files/2020/03/gender_responsive_urban_planning_design.pdf", "icon": "file-text", "source": "UN-Habitat"}
        ],
        6: [
            {"title": "UN SDG 6 - Clean Water and Sanitation", "url": "https://sdgs.un.org/goals/goal6", "icon": "globe", "source": "United Nations"},
            {"title": "Water Efficiency in Buildings", "url": "https://www.wbdg.org/resources/water-conservation", "icon": "droplet", "source": "Whole Building Design Guide"}
        ],
        7: [
            {"title": "UN SDG 7 - Affordable and Clean Energy", "url": "https://sdgs.un.org/goals/goal7", "icon": "globe", "source": "United Nations"},
            {"title": "Architecture 2030", "url": "https://architecture2030.org/", "icon": "sun", "source": "Architecture 2030 Initiative"}
        ],
        8: [
            {"title": "UN SDG 8 - Decent Work and Economic Growth", "url": "https://sdgs.un.org/goals/goal8", "icon": "globe", "source": "United Nations"},
            {"title": "Social and Economic Impact of Architecture", "url": "https://www.architecture.org.uk/explore-architecture/social-impact", "icon": "briefcase", "source": "RIBA"}
        ],
        9: [
            {"title": "UN SDG 9 - Industry, Innovation and Infrastructure", "url": "https://sdgs.un.org/goals/goal9", "icon": "globe", "source": "United Nations"},
            {"title": "Mass Timber Construction", "url": "https://www.thinkwood.com/mass-timber", "icon": "layers", "source": "Think Wood"}
        ],
        10: [
            {"title": "UN SDG 10 - Reduced Inequalities", "url": "https://sdgs.un.org/goals/goal10", "icon": "globe", "source": "United Nations"},
            {"title": "Universal Design Principles", "url": "https://universaldesign.ie/what-is-universal-design/", "icon": "users", "source": "Centre for Excellence in Universal Design"}
        ],
        11: [
            {"title": "UN SDG 11 - Sustainable Cities and Communities", "url": "https://sdgs.un.org/goals/goal11", "icon": "globe", "source": "United Nations"},
            {"title": "New Urban Agenda", "url": "https://habitat3.org/the-new-urban-agenda/", "icon": "home", "source": "UN-Habitat"}
        ],
        12: [
            {"title": "UN SDG 12 - Responsible Consumption and Production", "url": "https://sdgs.un.org/goals/goal12", "icon": "globe", "source": "United Nations"},
            {"title": "Circular Economy in Construction", "url": "https://www.ellenmacarthurfoundation.org/explore/built-environment", "icon": "refresh-cw", "source": "Ellen MacArthur Foundation"}
        ],
        13: [
            {"title": "UN SDG 13 - Climate Action", "url": "https://sdgs.un.org/goals/goal13", "icon": "globe", "source": "United Nations"},
            {"title": "AIA Climate Action Plan", "url": "https://www.aia.org/resources/6616-climate-action-plan", "icon": "cloud", "source": "American Institute of Architects"}
        ],
        14: [
            {"title": "UN SDG 14 - Life Below Water", "url": "https://sdgs.un.org/goals/goal14", "icon": "globe", "source": "United Nations"},
            {"title": "Sustainable Coastal Development", "url": "https://coastalresilience.org/", "icon": "droplet", "source": "The Nature Conservancy"}
        ],
        15: [
            {"title": "UN SDG 15 - Life on Land", "url": "https://sdgs.un.org/goals/goal15", "icon": "globe", "source": "United Nations"},
            {"title": "Biodiversity in Building Design", "url": "https://www.worldgbc.org/green-building-sustainable-development-goals-sdgs", "icon": "tree", "source": "World Green Building Council"}
        ],
        16: [
            {"title": "UN SDG 16 - Peace, Justice and Strong Institutions", "url": "https://sdgs.un.org/goals/goal16", "icon": "globe", "source": "United Nations"},
            {"title": "Crime Prevention Through Environmental Design", "url": "https://www.cpted.net/", "icon": "shield", "source": "International CPTED Association"}
        ],
        17: [
            {"title": "UN SDG 17 - Partnerships for the Goals", "url": "https://sdgs.un.org/goals/goal17", "icon": "globe", "source": "United Nations"},
            {"title": "UIA SDG Accord", "url": "https://www.uia-architectes.org/webApi/en/", "icon": "users", "source": "International Union of Architects"}
        ]
    }

    return render_template(
        'sdg_information_hub.html',
        title='SDG Information Hub',
        sdg_summaries=sdg_summaries,
        sdg_targets=sdg_targets,
        sdg_applications=sdg_applications,
        sdg_resources=sdg_resources
    )

@main_bp.route('/faq')
def faq():
    return render_template('faq.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/privacy-policy')
def privacy_policy():
    """Renders the privacy policy page."""
    return render_template('privacy_policy.html', title='Privacy Policy')

@main_bp.route('/super-secret-db-initialize/<path:secret_key>')
def initialize_database(secret_key):
    expected_secret = os.environ.get('DB_INIT_SECRET_KEY')
    if not expected_secret or secret_key != expected_secret:
        current_app.logger.warning("Unauthorized attempt to initialize database.")
        abort(403)

    try:
        with current_app.app_context():
            current_app.logger.info("Attempting to initialize database via secret endpoint...")
            # Use absolute path for alembic.ini
            alembic_ini_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../migrations/alembic.ini'))
            alembic_cfg = AlembicConfig(alembic_ini_path)
            alembic_cfg.set_main_option("sqlalchemy.url", current_app.config['SQLALCHEMY_DATABASE_URI'])
            alembic_command.upgrade(alembic_cfg, "head")
            current_app.logger.info("Alembic migrations applied via secret endpoint.")
            # Optionally, create views here if needed
        return "Database initialization process completed.", 200
    except Exception as e:
        current_app.logger.error(f"Error during database initialization via secret endpoint: {e}")
        return f"Error initializing database: {str(e)}", 500

@main_bp.route('/ping')
def ping():
    return "pong"

@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
