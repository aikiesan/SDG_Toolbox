-- Seed SDG Goals (17 goals)
-- First, check if we need to insert
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sdg_goals LIMIT 1) THEN
        INSERT INTO sdg_goals (number, name, description, color_code) VALUES
        (1, 'No Poverty', 'End poverty in all its forms everywhere', '#e5243b'),
        (2, 'Zero Hunger', 'End hunger, achieve food security and improved nutrition', '#dda63a'),
        (3, 'Good Health and Well-being', 'Ensure healthy lives and promote well-being for all', '#4c9f38'),
        (4, 'Quality Education', 'Ensure inclusive and equitable quality education', '#c5192d'),
        (5, 'Gender Equality', 'Achieve gender equality and empower all women and girls', '#ff3a21'),
        (6, 'Clean Water and Sanitation', 'Ensure availability and sustainable management of water', '#26bde2'),
        (7, 'Affordable and Clean Energy', 'Ensure access to affordable, reliable, sustainable energy', '#fcc30b'),
        (8, 'Decent Work and Economic Growth', 'Promote sustained, inclusive economic growth', '#a21942'),
        (9, 'Industry, Innovation and Infrastructure', 'Build resilient infrastructure, promote innovation', '#fd6925'),
        (10, 'Reduced Inequalities', 'Reduce inequality within and among countries', '#dd1367'),
        (11, 'Sustainable Cities and Communities', 'Make cities and human settlements inclusive and sustainable', '#fd9d24'),
        (12, 'Responsible Consumption and Production', 'Ensure sustainable consumption and production patterns', '#bf8b2e'),
        (13, 'Climate Action', 'Take urgent action to combat climate change', '#3f7e44'),
        (14, 'Life Below Water', 'Conserve and sustainably use the oceans and marine resources', '#0a97d9'),
        (15, 'Life on Land', 'Protect, restore and promote sustainable use of ecosystems', '#56c02b'),
        (16, 'Peace, Justice and Strong Institutions', 'Promote peaceful and inclusive societies', '#00689d'),
        (17, 'Partnerships for the Goals', 'Strengthen the means of implementation', '#19486a');
    END IF;
END $$;

-- Seed SDG Questions (31 questions)
-- Questions are distributed across the 7 SDG categories used in the assessment
INSERT INTO sdg_questions (id, text, type, sdg_id, max_score, display_order) VALUES
-- Section 1: Impact & Resilience (SDG 1, 2, 3, 4, 5)
(1, 'To what extent does your project adapt to future challenges?', 'radio', 1, 5.0, 1),
(2, 'Which resilience features are incorporated?', 'checkbox', 1, 5.0, 2),
(3, 'How does your project address food security concerns?', 'radio', 2, 5.0, 3),
(4, 'Which food security strategies are implemented?', 'checkbox', 2, 5.0, 4),
(5, 'Which health and well-being features does your project include?', 'checkbox', 3, 5.0, 5),
(6, 'To what extent does your project promote educational opportunities?', 'radio', 4, 5.0, 6),
(7, 'Which educational features are included?', 'checkbox', 4, 5.0, 7),
(8, 'How does your project promote gender equality?', 'radio', 5, 5.0, 8),
(9, 'Which gender equality measures are implemented?', 'checkbox', 5, 5.0, 9),

-- Section 2: Resource Management (SDG 6, 7)
(10, 'How effectively does your project manage water resources?', 'radio', 6, 5.0, 10),
(11, 'Which water management features are included?', 'checkbox', 6, 5.0, 11),
(12, 'To what extent does your project use renewable energy?', 'radio', 7, 5.0, 12),
(13, 'Which renewable energy technologies are implemented?', 'checkbox', 7, 5.0, 13),

-- Section 3: Economic & Social (SDG 8, 9, 10)
(14, 'How does your project create economic opportunities?', 'radio', 8, 5.0, 14),
(15, 'Which economic development strategies are implemented?', 'checkbox', 8, 5.0, 15),
(16, 'To what extent does your project promote innovation?', 'radio', 9, 5.0, 16),
(17, 'Which innovative features are included?', 'checkbox', 9, 5.0, 17),
(18, 'How does your project address inequality?', 'radio', 10, 5.0, 18),
(19, 'Which inequality reduction measures are implemented?', 'checkbox', 10, 5.0, 19),

-- Section 4: Urban & Community (SDG 11)
(20, 'How sustainable is your urban design?', 'radio', 11, 5.0, 20),
(21, 'Which sustainable urban features are included?', 'checkbox', 11, 5.0, 21),

-- Section 5: Consumption & Production (SDG 12)
(22, 'To what extent does your project follow circular economy principles?', 'radio', 12, 5.0, 22),
(23, 'Which circular economy strategies are implemented?', 'checkbox', 12, 5.0, 23),

-- Section 6: Environment (SDG 13, 14, 15)
(24, 'How does your project address climate change?', 'radio', 13, 5.0, 24),
(25, 'Which climate action measures are implemented?', 'checkbox', 13, 5.0, 25),
(26, 'To what extent does your project protect water ecosystems?', 'radio', 14, 5.0, 26),
(27, 'Which water ecosystem protection measures are included?', 'checkbox', 14, 5.0, 27),
(28, 'How does your project protect terrestrial ecosystems?', 'radio', 15, 5.0, 28),
(29, 'Which land ecosystem protection measures are implemented?', 'checkbox', 15, 5.0, 29),

-- Section 7: Governance & Partnerships (SDG 16, 17)
(30, 'Which governance and peace-building features are included?', 'checkbox', 16, 5.0, 30),
(31, 'Which partnership strategies are implemented?', 'checkbox', 17, 5.0, 31)
ON CONFLICT (id) DO UPDATE SET text = EXCLUDED.text;
