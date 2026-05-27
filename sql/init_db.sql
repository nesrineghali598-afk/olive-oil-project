-- ============================================================
--  init_db.sql — Projet Huile d'Olive International
--  MSc2 Manager Data Marketing — INSEEC 2026
--  Source : Conseil Oléicole International (COI/IOC)
--  Toutes les tables ont 30+ lignes
-- ============================================================

CREATE DATABASE olive_oil_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
 
USE olive_oil_db;
-- ============================================================
-- TABLE 1 : pays_producteurs (30 lignes)
-- Pays membres et non-membres du COI producteurs d'huile d'olive
-- ============================================================
CREATE TABLE pays_producteurs (
  id_pays         INT AUTO_INCREMENT PRIMARY KEY,
  nom_pays        VARCHAR(100)  NOT NULL,
  region          VARCHAR(50)   NOT NULL,
  production_2024 DECIMAL(10,2) COMMENT 'Milliers de tonnes — source COI 2024/25',
  membre_coi      TINYINT(1)    DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO pays_producteurs (nom_pays, region, production_2024, membre_coi) VALUES
  ('Espagne',           'Europe Méditerranée',        1419.00, 1),  -- 1
  ('Italie',            'Europe Méditerranée',          248.00, 1),  -- 2
  ('Grèce',             'Europe Méditerranée',          250.00, 1),  -- 3
  ('Portugal',          'Europe Méditerranée',          177.00, 1),  -- 4
  ('Tunisie',           'Afrique du Nord',              340.00, 1),  -- 5
  ('Turquie',           'Moyen-Orient',                 505.00, 1),  -- 6
  ('Maroc',             'Afrique du Nord',              130.00, 1),  -- 7
  ('Syrie',             'Moyen-Orient',                  90.00, 1),  -- 8
  ('Algérie',           'Afrique du Nord',               60.00, 1),  -- 9
  ('Jordanie',          'Moyen-Orient',                  25.00, 1),  -- 10
  ('Argentine',         'Amérique du Sud',               35.00, 0),  -- 11
  ('Chili',             'Amérique du Sud',               22.00, 0),  -- 12
  ('Croatie',           'Europe Méditerranée',           10.00, 1),  -- 13
  ('Chypre',            'Europe Méditerranée',            8.50, 1),  -- 14
  ('France',            'Europe Méditerranée',            5.20, 1),  -- 15
  ('Albanie',           'Europe Méditerranée',           12.00, 1),  -- 16
  ('Égypte',            'Afrique du Nord',               37.00, 1),  -- 17
  ('Libye',             'Afrique du Nord',               15.00, 1),  -- 18
  ('Liban',             'Moyen-Orient',                  18.00, 1),  -- 19
  ('Israël',            'Moyen-Orient',                  20.00, 1),  -- 20
  ('Palestine',         'Moyen-Orient',                  14.00, 1),  -- 21
  ('Iran',              'Moyen-Orient',                  11.00, 0),  -- 22
  ('USA',               'Amérique du Nord',              16.00, 0),  -- 23
  ('Mexique',           'Amérique du Nord',               4.50, 0),  -- 24
  ('Pérou',             'Amérique du Sud',               19.00, 0),  -- 25
  ('Australie',         'Océanie',                       21.00, 0),  -- 26
  ('Nouvelle-Zélande',  'Océanie',                        2.50, 0),  -- 27
  ('Afrique du Sud',    'Afrique Sub-saharienne',         9.00, 0),  -- 28
  ('Chine',             'Asie',                           6.50, 0),  -- 29
  ('Inde',              'Asie',                           1.20, 0);  -- 30

-- ============================================================
-- TABLE 2 : producteurs (30 lignes)
-- Domaines oléicoles liés à un pays producteur
-- ============================================================
CREATE TABLE producteurs (
  id_producteur INT AUTO_INCREMENT PRIMARY KEY,
  nom_domaine   VARCHAR(150) NOT NULL,
  certification VARCHAR(50)  COMMENT 'AOP, IGP, Bio, Standard',
  ville         VARCHAR(100),
  id_pays       INT NOT NULL,
  CONSTRAINT fk_producteur_pays
    FOREIGN KEY (id_pays) REFERENCES pays_producteurs(id_pays)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO producteurs (nom_domaine, certification, ville, id_pays) VALUES
  ('Domaine Oleica Andaluz',     'AOP',      'Jaén',         1),   -- 1
  ('Finca Sierra Nevada',        'Bio',      'Grenade',      1),   -- 2
  ('Tenuta Bari Oro',            'AOP',      'Bari',         2),   -- 3
  ('Frantoio della Toscana',     'Bio',      'Florence',     2),   -- 4
  ('Domaine Kalamata Premium',   'AOP',      'Kalamata',     3),   -- 5
  ('Cretan Gold Estate',         'Standard', 'Héraklion',    3),   -- 6
  ('Herdade do Alentejo',        'IGP',      'Évora',        4),   -- 7
  ('Domaine Sfax Excellence',    'Bio',      'Sfax',         5),   -- 8
  ('Zaitouna Organic Farm',      'Bio',      'Tunis',        5),   -- 9
  ('Akdeniz Olive Press',        'Standard', 'Izmir',        6),   -- 10
  ('Domaine Meknès Prestige',    'IGP',      'Meknès',       7),   -- 11
  ('Atlas Mountain Olive',       'Bio',      'Marrakech',    7),   -- 12
  ('Istria Gold Estate',         'AOP',      'Rovinj',       13),  -- 13
  ('Cyprus Aphrodite Oils',      'Bio',      'Limassol',     14),  -- 14
  ('Moulin de Haute-Provence',   'AOP',      'Manosque',     15),  -- 15
  ('Domaine Baux-de-Provence',   'AOP',      'Les Baux',     15),  -- 16
  ('Albanian Olive Trust',       'Standard', 'Vlorë',        16),  -- 17
  ('Alexandria Premium Farm',    'Bio',      'Alexandrie',   17),  -- 18
  ('Nile Delta Olive Press',     'Standard', 'Le Caire',     17),  -- 19
  ('Tripoli Heritage Oils',      'Standard', 'Tripoli',      18),  -- 20
  ('Galilee Organic Estate',     'Bio',      'Nazareth',     20),  -- 21 (Israël)
  ('Ramallah Heritage Farm',     'IGP',      'Ramallah',     21),  -- 22 (Palestine)
  ('Persian Olive Gardens',      'Standard', 'Ispahan',      22),  -- 23 (Iran)
  ('California Olive Ranch',     'Bio',      'Chico',        23),  -- 24 (USA)
  ('Oaxaca Grove Mexico',        'Standard', 'Oaxaca',       24),  -- 25 (Mexique)
  ('Atacama Premium Oils',       'Bio',      'Santiago',     25),  -- 26 (Pérou)
  ('Grove Estate Australia',     'IGP',      'Adelaide',     26),  -- 27 (Australie)
  ('New Zealand Olives Ltd',     'Bio',      'Marlborough',  27),  -- 28 (Nouvelle-Zélande)
  ('Cape Olive Farm SA',         'Standard', 'Le Cap',       28),  -- 29 (Afrique du Sud)
  ('Yunnan Olive Project',       'Standard', 'Kunming',      29);  -- 30 (Chine)

-- ============================================================
-- TABLE 3 : produits (30 lignes)
-- Huiles d'olive : Extra Vierge, Vierge, Raffinée, Pomace
-- ============================================================
CREATE TABLE produits (
  id_produit    INT AUTO_INCREMENT PRIMARY KEY,
  nom_produit   VARCHAR(150)  NOT NULL,
  type_huile    ENUM('Extra Vierge','Vierge','Raffinée','Pomace') NOT NULL,
  acidite       DECIMAL(4,2)  COMMENT 'Taux acidité % — Extra Vierge < 0.8%',
  prix_litre    DECIMAL(10,2) NOT NULL,
  annee_recolte INT,
  contenance_ml INT           DEFAULT 750 COMMENT '250, 500, 750, 1000, 5000',
  appellation   VARCHAR(100),
  id_producteur INT NOT NULL,
  CONSTRAINT fk_produit_producteur
    FOREIGN KEY (id_producteur) REFERENCES producteurs(id_producteur)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO produits (nom_produit, type_huile, acidite, prix_litre, annee_recolte, contenance_ml, appellation, id_producteur) VALUES
  ('Oleica Andaluz Picual Premium',  'Extra Vierge', 0.25, 18.50, 2024,  750, 'AOP Jaén',               1),  -- 1
  ('Sierra Nevada Arbequina Bio',    'Extra Vierge', 0.18, 22.00, 2024,  500, 'Bio Andalousie',          2),  -- 2
  ('Tenuta Bari Coratina',           'Extra Vierge', 0.35, 24.00, 2023,  750, 'AOP Terra di Bari',       3),  -- 3
  ('Toscana Frantoio IGP',           'Extra Vierge', 0.20, 28.00, 2024,  250, 'IGP Toscane',             4),  -- 4
  ('Kalamata Protected Origin',      'Extra Vierge', 0.30, 26.50, 2024,  750, 'AOP Kalamata',            5),  -- 5
  ('Cretan Koroneiki Classic',       'Extra Vierge', 0.45, 16.00, 2024, 1000, 'Crète',                   6),  -- 6
  ('Alentejo Galega Premium',        'Extra Vierge', 0.28, 21.00, 2024,  750, 'IGP Alentejo',            7),  -- 7
  ('Sfax Chetoui Excellence',        'Extra Vierge', 0.22, 19.00, 2024,  750, 'Sfax Tunisie',            8),  -- 8
  ('Zaitouna Organic Blend',         'Extra Vierge', 0.40, 17.50, 2023,  500, 'Bio Tunisie',             9),  -- 9
  ('Akdeniz Memecik Soft',           'Vierge',       0.90, 11.00, 2024, 1000, 'Izmir Turquie',          10),  -- 10
  ('Meknès Atlas Picholine',         'Extra Vierge', 0.35, 20.00, 2024,  750, 'IGP Meknès Maroc',       11),  -- 11
  ('Atlas Mountain Menara Bio',      'Extra Vierge', 0.30, 23.00, 2024,  500, 'Bio Atlas',              12),  -- 12
  ('Oleica Classique Vierge',        'Vierge',       1.20,  9.00, 2024, 5000, NULL,                      1),  -- 13
  ('Tenuta Bari Raffinée Pro',       'Raffinée',     0.05,  7.50, 2024, 5000, NULL,                      3),  -- 14
  ('Cretan Pomace Industrial',       'Pomace',       0.80,  4.50, 2024, 5000, NULL,                      6),  -- 15
  ('Istria Buza Prestige',           'Extra Vierge', 0.20, 32.00, 2024,  250, 'AOP Istrie Croatie',     13),  -- 16
  ('Cyprus Aphrodite Gold',          'Extra Vierge', 0.25, 29.00, 2024,  500, 'Bio Chypre',             14),  -- 17
  ('Haute-Provence AOP Classic',     'Extra Vierge', 0.30, 27.00, 2024,  750, 'AOP Haute-Provence',     15),  -- 18
  ('Baux-de-Provence Grand Cru',     'Extra Vierge', 0.18, 38.00, 2024,  250, 'AOP Baux-de-Provence',   16),  -- 19
  ('Albanian Kalinjot Pure',         'Vierge',       0.85, 10.50, 2024, 1000, 'Albanie',                17),  -- 20
  ('Alexandria Desert Gold',         'Extra Vierge', 0.40, 15.00, 2024,  750, 'Égypte',                 18),  -- 21
  ('Nile Delta Blend Standard',      'Vierge',       1.10,  8.00, 2024, 5000, NULL,                     19),  -- 22
  ('Galilee Souri Bio Premium',      'Extra Vierge', 0.22, 31.00, 2024,  500, 'Bio Galilée Israël',     21),  -- 23
  ('Ramallah Rumi Heritage',         'Extra Vierge', 0.35, 24.50, 2023,  750, 'Palestine',              22),  -- 24
  ('California Ranch Arbosana',      'Extra Vierge', 0.28, 26.00, 2024,  750, 'Californie USA',         24),  -- 25
  ('Atacama Arbequina Reserve',      'Extra Vierge', 0.32, 23.00, 2024,  500, 'Vallée de Colchagua',    26),  -- 26
  ('Grove Estate Frantoio AU',       'Extra Vierge', 0.38, 28.00, 2024,  750, 'Australie-Méridionale',  27),  -- 27
  ('NZ Leccino Single Estate',       'Extra Vierge', 0.26, 34.00, 2024,  250, 'Nouvelle-Zélande',       28),  -- 28
  ('Cape Farm South African Blend',  'Extra Vierge', 0.42, 19.00, 2024,  750, 'Afrique du Sud',         29),  -- 29
  ('Oleica Bulk Professionnel',      'Raffinée',     0.05,  6.00, 2024, 5000, NULL,                      1);  -- 30

-- ============================================================
-- TABLE 4 : clients (30 lignes)
-- Distributeurs et acheteurs internationaux
-- ============================================================
CREATE TABLE clients (
  id_client        INT AUTO_INCREMENT PRIMARY KEY,
  nom_societe      VARCHAR(150) NOT NULL,
  pays_client      VARCHAR(100) NOT NULL,
  email            VARCHAR(150) UNIQUE NOT NULL,
  segment          ENUM('Gold','Silver','Bronze') DEFAULT 'Bronze',
  date_inscription DATE         DEFAULT (CURRENT_DATE),
  type_client      ENUM('Distributeur','Epicerie Fine','GMS','Restauration') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO clients (nom_societe, pays_client, email, segment, date_inscription, type_client) VALUES
  ('Gourmet France Distribution',  'France',         'contact@gourmetfrance.fr',   'Gold',   '2022-03-15', 'Distributeur'),   -- 1
  ('La Belle Épicerie Paris',      'France',         'info@belleepicerie.fr',       'Silver', '2022-07-20', 'Epicerie Fine'),  -- 2
  ('NaturaBio Germany GmbH',       'Allemagne',      'info@naturabio.de',           'Gold',   '2021-11-10', 'Distributeur'),   -- 3
  ('Feinkost München',             'Allemagne',      'orders@feinkost-muc.de',      'Silver', '2023-01-05', 'Epicerie Fine'),  -- 4
  ('Olive World UK Ltd',           'Royaume-Uni',    'sales@oliveworld.co.uk',      'Gold',   '2021-06-22', 'Distributeur'),   -- 5
  ('Selfridges Food Hall',         'Royaume-Uni',    'food@selfridges.com',         'Silver', '2023-04-18', 'Epicerie Fine'),  -- 6
  ('Mediterranean Foods USA',      'États-Unis',     'orders@medfoods.us',          'Gold',   '2020-09-30', 'Distributeur'),   -- 7
  ('Whole Foods Market West',      'États-Unis',     'buyer@wholefoodswest.com',    'Silver', '2022-11-12', 'GMS'),            -- 8
  ('Tokyo Olive Import Co.',       'Japon',          'import@tokyoolive.jp',        'Silver', '2023-03-01', 'Distributeur'),   -- 9
  ('Kyoto Delicatessen',           'Japon',          'kyoto@deli.jp',               'Bronze', '2024-01-10', 'Epicerie Fine'),  -- 10
  ('Nordic Gourmet Sweden AB',     'Suède',          'info@nordicgourmet.se',       'Silver', '2022-08-14', 'Distributeur'),   -- 11
  ('Coop Sverige Premium',         'Suède',          'premium@coop.se',             'Bronze', '2023-09-20', 'GMS'),            -- 12
  ('Canada Organic Trade',         'Canada',         'trade@canorganic.ca',         'Silver', '2022-05-05', 'Distributeur'),   -- 13
  ('Épicerie Montréal Fine',       'Canada',         'fine@epiceriemtl.ca',         'Bronze', '2023-12-01', 'Epicerie Fine'),  -- 14
  ('Lux Food Benelux BV',          'Pays-Bas',       'orders@luxfood.nl',           'Gold',   '2021-02-28', 'Distributeur'),   -- 15
  ('Albert Heijn Premium',         'Pays-Bas',       'premium@ah.nl',               'Silver', '2022-10-15', 'GMS'),            -- 16
  ('Australia Olive Imports',      'Australie',      'info@ausolive.com.au',        'Silver', '2023-06-07', 'Distributeur'),   -- 17
  ('Woolworths Gourmet AU',        'Australie',      'gourmet@woolworths.com.au',   'Bronze', '2024-02-15', 'GMS'),            -- 18
  ('China Premium Foods Beijing',  'Chine',          'premium@cpfoods.cn',          'Silver', '2023-07-20', 'Distributeur'),   -- 19
  ('Shanghai Gourmet Club',        'Chine',          'info@shgourmet.cn',           'Bronze', '2024-03-10', 'Epicerie Fine'),  -- 20
  ('Delhaize Belgium Premium',     'Belgique',       'premium@delhaize.be',         'Silver', '2023-02-10', 'GMS'),            -- 21
  ('Swiss Gourmet Zurich AG',      'Suisse',         'orders@swissgourmet.ch',      'Silver', '2022-12-05', 'Epicerie Fine'),  -- 22
  ('El Corte Inglés Gourmet',      'Espagne',        'gourmet@elcorteingles.es',    'Bronze', '2024-01-20', 'GMS'),            -- 23
  ('Eataly Milano Import',         'Italie',         'import@eataly.it',            'Gold',   '2021-08-15', 'Distributeur'),   -- 24
  ('Dubai Luxury Foods DMCC',      'Émirats',        'luxury@dubaifood.ae',         'Silver', '2023-05-30', 'Epicerie Fine'),  -- 25
  ('Singapore Premium Trade',      'Singapour',      'trade@sgpremium.sg',          'Silver', '2023-08-22', 'Distributeur'),   -- 26
  ('Seoul Fine Food Korea',        'Corée du Sud',   'fine@seoulfood.kr',           'Bronze', '2024-02-01', 'Epicerie Fine'),  -- 27
  ('Brasília Gourmet Import',      'Brésil',         'import@brgourmet.com.br',     'Bronze', '2023-11-14', 'Distributeur'),   -- 28
  ('Mexico City Deli Trade',       'Mexique',        'deli@mxfood.mx',              'Bronze', '2024-03-05', 'Epicerie Fine'),  -- 29
  ('Johannesburg Olive Co.',       'Afrique du Sud', 'info@jholiveco.co.za',        'Bronze', '2024-04-18', 'Distributeur');   -- 30

-- ============================================================
-- TABLE 5 : commandes (56 lignes)
-- ============================================================
CREATE TABLE commandes (
  id_commande    INT AUTO_INCREMENT PRIMARY KEY,
  id_client      INT NOT NULL,
  date_commande  DATETIME      DEFAULT CURRENT_TIMESTAMP,
  montant_total  DECIMAL(10,2) NOT NULL,
  statut         ENUM('En cours','Expédiée','Livrée','Annulée') DEFAULT 'En cours',
  pays_livraison VARCHAR(100),
  CONSTRAINT fk_commande_client
    FOREIGN KEY (id_client) REFERENCES clients(id_client)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO commandes (id_client, date_commande, montant_total, statut, pays_livraison) VALUES
  (1,  '2024-01-10 09:00:00',  3700.00, 'Livrée',   'France'),         -- 1
  (1,  '2024-03-22 14:00:00',  5200.00, 'Livrée',   'France'),         -- 2
  (1,  '2024-07-05 10:30:00',  4100.00, 'Livrée',   'France'),         -- 3
  (1,  '2024-11-18 08:00:00',  6800.00, 'Livrée',   'France'),         -- 4
  (2,  '2024-02-14 11:00:00',   850.00, 'Livrée',   'France'),         -- 5
  (2,  '2024-09-20 15:00:00',   920.00, 'Livrée',   'France'),         -- 6
  (3,  '2024-01-05 08:00:00',  8500.00, 'Livrée',   'Allemagne'),      -- 7
  (3,  '2024-04-12 09:00:00',  7200.00, 'Livrée',   'Allemagne'),      -- 8
  (3,  '2024-08-30 10:00:00',  9100.00, 'Livrée',   'Allemagne'),      -- 9
  (3,  '2024-12-01 11:00:00',  6300.00, 'Expédiée', 'Allemagne'),      -- 10
  (4,  '2024-03-18 13:00:00',   450.00, 'Livrée',   'Allemagne'),      -- 11
  (5,  '2024-02-01 09:00:00', 12000.00, 'Livrée',   'Royaume-Uni'),    -- 12
  (5,  '2024-05-15 14:00:00', 10500.00, 'Livrée',   'Royaume-Uni'),    -- 13
  (5,  '2024-09-08 10:00:00', 11800.00, 'Livrée',   'Royaume-Uni'),    -- 14
  (5,  '2024-12-20 09:00:00', 13200.00, 'En cours', 'Royaume-Uni'),    -- 15
  (6,  '2024-06-22 12:00:00',   780.00, 'Livrée',   'Royaume-Uni'),    -- 16
  (7,  '2024-01-20 08:30:00', 15000.00, 'Livrée',   'États-Unis'),     -- 17
  (7,  '2024-04-10 09:00:00', 18500.00, 'Livrée',   'États-Unis'),     -- 18
  (7,  '2024-07-25 10:00:00', 17200.00, 'Livrée',   'États-Unis'),     -- 19
  (7,  '2024-10-30 11:00:00', 21000.00, 'Expédiée', 'États-Unis'),     -- 20
  (8,  '2024-08-14 13:00:00',  3200.00, 'Livrée',   'États-Unis'),     -- 21
  (9,  '2024-03-05 09:00:00',  4500.00, 'Livrée',   'Japon'),          -- 22
  (9,  '2024-09-12 10:00:00',  5200.00, 'Livrée',   'Japon'),          -- 23
  (10, '2024-11-01 14:00:00',   380.00, 'Livrée',   'Japon'),          -- 24
  (11, '2024-02-28 08:00:00',  3800.00, 'Livrée',   'Suède'),          -- 25
  (11, '2024-06-15 09:00:00',  4100.00, 'Livrée',   'Suède'),          -- 26
  (12, '2024-10-05 11:00:00',   650.00, 'Livrée',   'Suède'),          -- 27
  (13, '2024-04-20 10:00:00',  2900.00, 'Livrée',   'Canada'),         -- 28
  (13, '2024-10-18 14:00:00',  3400.00, 'Expédiée', 'Canada'),         -- 29
  (14, '2024-07-11 12:00:00',   490.00, 'Livrée',   'Canada'),         -- 30
  (15, '2024-01-15 08:00:00',  9200.00, 'Livrée',   'Pays-Bas'),       -- 31
  (15, '2024-05-20 09:00:00',  8800.00, 'Livrée',   'Pays-Bas'),       -- 32
  (15, '2024-09-25 10:00:00', 10500.00, 'Livrée',   'Pays-Bas'),       -- 33
  (16, '2024-06-30 13:00:00',  1800.00, 'Livrée',   'Pays-Bas'),       -- 34
  (17, '2024-05-08 09:00:00',  2600.00, 'Livrée',   'Australie'),      -- 35
  (17, '2024-11-14 11:00:00',  3100.00, 'Expédiée', 'Australie'),      -- 36
  (18, '2024-08-22 14:00:00',   420.00, 'Livrée',   'Australie'),      -- 37
  (19, '2024-06-10 08:00:00',  5800.00, 'Livrée',   'Chine'),          -- 38
  (19, '2024-11-05 10:00:00',  6200.00, 'En cours', 'Chine'),          -- 39
  (20, '2024-12-01 12:00:00',   750.00, 'En cours', 'Chine'),          -- 40
  (21, '2024-04-10 09:00:00',  1200.00, 'Livrée',   'Belgique'),       -- 41
  (21, '2024-09-15 10:00:00',  1450.00, 'Livrée',   'Belgique'),       -- 42
  (22, '2024-05-20 11:00:00',   980.00, 'Livrée',   'Suisse'),         -- 43
  (22, '2024-10-08 14:00:00',  1100.00, 'Expédiée', 'Suisse'),         -- 44
  (23, '2024-06-12 09:00:00',   560.00, 'Livrée',   'Espagne'),        -- 45
  (24, '2024-03-25 08:00:00',  4200.00, 'Livrée',   'Italie'),         -- 46
  (24, '2024-08-18 10:00:00',  3800.00, 'Livrée',   'Italie'),         -- 47
  (24, '2024-12-05 09:00:00',  5100.00, 'En cours', 'Italie'),         -- 48
  (25, '2024-05-14 11:00:00',  2200.00, 'Livrée',   'Émirats'),        -- 49
  (25, '2024-11-20 13:00:00',  2800.00, 'Expédiée', 'Émirats'),        -- 50
  (26, '2024-07-01 09:00:00',  1900.00, 'Livrée',   'Singapour'),      -- 51
  (26, '2024-11-25 10:00:00',  2100.00, 'En cours', 'Singapour'),      -- 52
  (27, '2024-08-10 08:00:00',   650.00, 'Livrée',   'Corée du Sud'),   -- 53
  (28, '2024-09-05 11:00:00',  1400.00, 'Livrée',   'Brésil'),         -- 54
  (29, '2024-10-20 10:00:00',   480.00, 'Livrée',   'Mexique'),        -- 55
  (30, '2024-11-12 09:00:00',   720.00, 'Livrée',   'Afrique du Sud'); -- 56

-- ============================================================
-- TABLE 6 : commande_produit — RELATION MANY-TO-MANY
-- Une commande peut contenir plusieurs produits
-- Un produit peut figurer dans plusieurs commandes
-- ============================================================
CREATE TABLE commande_produit (
  id_commande     INT NOT NULL,
  id_produit      INT NOT NULL,
  quantite_litres INT NOT NULL DEFAULT 1,
  prix_unitaire   DECIMAL(10,2) NOT NULL COMMENT 'Prix au moment de la commande',
  PRIMARY KEY (id_commande, id_produit),
  CONSTRAINT fk_cp_commande
    FOREIGN KEY (id_commande) REFERENCES commandes(id_commande)
    ON DELETE CASCADE,
  CONSTRAINT fk_cp_produit
    FOREIGN KEY (id_produit) REFERENCES produits(id_produit)
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO commande_produit (id_commande, id_produit, quantite_litres, prix_unitaire) VALUES
  -- Commandes 1-10 (Clients France & Allemagne)
  (1,  1, 100, 18.50), (1,  5,  80, 26.50), (1,  8,  60, 19.00),
  (2,  1, 150, 18.50), (2,  3,  80, 24.00), (2,  4,  30, 28.00),
  (3,  5, 100, 26.50), (3,  7,  80, 21.00), (3,  8,  60, 19.00),
  (4,  1, 200, 18.50), (4,  2, 100, 22.00), (4,  3,  80, 24.00),
  (5,  4,  10, 28.00), (5,  5,  15, 26.50), (5, 11,  10, 20.00),
  (6,  4,  12, 28.00), (6, 12,  10, 23.00),
  (7,  1, 200, 18.50), (7,  3, 150, 24.00), (7,  5, 100, 26.50),
  (8,  2, 150, 22.00), (8,  7, 100, 21.00), (8, 11, 100, 20.00),
  (9,  1, 250, 18.50), (9,  3, 100, 24.00), (9, 13, 200,  9.00),
  (10, 2, 150, 22.00), (10, 5, 100, 26.50), (10, 8,  80, 19.00),
  -- Commandes 11-20 (Clients Royaume-Uni & USA)
  (11, 11,  10, 20.00), (11, 12,   8, 23.00),
  (12,  1, 300, 18.50), (12,  3, 200, 24.00), (12,  5, 150, 26.50),
  (13,  1, 250, 18.50), (13,  2, 150, 22.00), (13,  4, 100, 28.00),
  (14,  3, 200, 24.00), (14,  5, 200, 26.50), (14,  7, 100, 21.00),
  (15,  1, 300, 18.50), (15,  3, 250, 24.00), (15,  5, 200, 26.50),
  (16,  4,  12, 28.00), (16, 11,  10, 20.00),
  (17,  1, 400, 18.50), (17,  2, 200, 22.00), (17,  3, 200, 24.00),
  (18,  1, 500, 18.50), (18,  5, 300, 26.50), (18,  8, 200, 19.00),
  (19,  2, 400, 22.00), (19,  7, 300, 21.00), (19, 13, 500,  9.00),
  (20,  1, 600, 18.50), (20,  3, 300, 24.00), (20,  5, 250, 26.50),
  -- Commandes 21-30 (Clients USA, Japon, Suède, Canada)
  (21,  6,  80, 16.00), (21, 13, 200,  9.00), (21, 14, 100,  7.50),
  (22,  5,  80, 26.50), (22,  8,  70, 19.00), (22, 11,  50, 20.00),
  (23,  4,  60, 28.00), (23,  5,  80, 26.50), (23, 12,  30, 23.00),
  (24, 11,   8, 20.00), (24, 12,   6, 23.00),
  (25,  1, 100, 18.50), (25,  8,  80, 19.00), (25, 11,  60, 20.00),
  (26,  5, 100, 26.50), (26,  7,  80, 21.00), (26, 12,  50, 23.00),
  (27,  6,  20, 16.00), (27, 13,  30,  9.00),
  (28,  5,  80, 26.50), (28,  8,  60, 19.00), (28, 11,  40, 20.00),
  (29,  1, 100, 18.50), (29,  3,  80, 24.00), (29,  8,  60, 19.00),
  (30,  4,   8, 28.00), (30, 12,   5, 23.00),
  -- Commandes 31-40 (Clients Pays-Bas, Australie, Chine)
  (31,  1, 250, 18.50), (31,  3, 150, 24.00), (31,  5, 100, 26.50),
  (32,  2, 200, 22.00), (32,  7, 150, 21.00), (32,  8, 100, 19.00),
  (33,  1, 300, 18.50), (33,  3, 200, 24.00), (33,  5, 150, 26.50),
  (34,  4,  30, 28.00), (34,  6,  40, 16.00), (34, 11,  20, 20.00),
  (35,  5,  70, 26.50), (35,  8,  60, 19.00), (35, 12,  30, 23.00),
  (36,  1,  80, 18.50), (36,  8,  70, 19.00), (36, 11,  50, 20.00),
  (37,  6,  10, 16.00), (37, 13,  20,  9.00),
  (38,  5, 150, 26.50), (38,  8, 100, 19.00), (38, 11,  80, 20.00),
  (39,  1, 150, 18.50), (39,  5, 120, 26.50), (39,  8, 100, 19.00),
  (40,  4,  10, 28.00), (40, 11,  10, 20.00), (40, 12,   8, 23.00),
  -- Commandes 41-56 (Nouveaux clients 21-30)
  (41,  1,  30, 18.50), (41,  8,  25, 19.00), (41, 11,  15, 20.00),
  (42,  5,  30, 26.50), (42,  8,  25, 19.00), (42, 16,  10, 32.00),
  (43,  4,  15, 28.00), (43, 17,  15, 29.00),
  (44,  7,  20, 21.00), (44, 18,  10, 27.00),
  (45,  6,  30, 16.00), (45, 13,  20,  9.00),
  (46,  1,  80, 18.50), (46,  3,  60, 24.00), (46, 19,  10, 38.00),
  (47,  5,  70, 26.50), (47,  7,  50, 21.00), (47, 17,  15, 29.00),
  (48,  1,  90, 18.50), (48,  3,  80, 24.00), (48,  5,  60, 26.50),
  (49, 18,  30, 27.00), (49, 16,  20, 32.00), (49, 21,  20, 15.00),
  (50,  4,  40, 28.00), (50, 18,  30, 27.00), (50, 16,  20, 32.00),
  (51,  5,  40, 26.50), (51,  8,  30, 19.00), (51, 11,  25, 20.00),
  (52,  1,  50, 18.50), (52,  5,  40, 26.50), (52, 16,  15, 32.00),
  (53, 11,  15, 20.00), (53, 17,  10, 29.00),
  (54,  8,  35, 19.00), (54, 11,  25, 20.00), (54, 24,  10, 24.50),
  (55,  6,  20, 16.00), (55, 13,  30,  9.00),
  (56, 11,  20, 20.00), (56, 25,  15, 26.00);

-- ============================================================
-- VÉRIFICATION FINALE — Compte les lignes par table
-- ============================================================
SELECT 'pays_producteurs' AS table_name, COUNT(*) AS nb_lignes FROM pays_producteurs
UNION ALL SELECT 'producteurs',      COUNT(*) FROM producteurs
UNION ALL SELECT 'produits',         COUNT(*) FROM produits
UNION ALL SELECT 'clients',          COUNT(*) FROM clients
UNION ALL SELECT 'commandes',        COUNT(*) FROM commandes
UNION ALL SELECT 'commande_produit', COUNT(*) FROM commande_produit;