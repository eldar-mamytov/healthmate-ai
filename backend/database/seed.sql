-- Initial Diseases Data
INSERT INTO diseases (name, description, confidence_score) VALUES
('Common Cold', 'A viral infection of your nose and throat (upper respiratory tract). It''s usually harmless, although it might not feel that way. Many types of viruses can cause a common cold.', 0.8),
('Influenza (Flu)', 'A contagious respiratory illness caused by influenza viruses that infect the nose, throat, and sometimes the lungs. It can cause mild to severe illness, and at times can lead to death.', 0.9),
('Allergies', 'An immune system response to a foreign substance that''s not typically harmful to your body. These foreign substances are called allergens.', 0.7),
('Headache (Tension)', 'A common type of headache that causes mild to moderate pain or pressure in the head, often described as a tight band around the head. Usually related to stress or muscle tension.', 0.6),
('Strep Throat', 'A bacterial infection that can make your throat feel sore and scratchy. If left untreated, strep throat can cause serious complications.', 0.95),
('General Unwell Feeling', 'A non-specific feeling of discomfort, illness, or fatigue, not clearly pointing to a specific acute disease. Suggests general malaise.', 0.3); -- Lower confidence as it's vague

-- Initial Symptoms Data
INSERT INTO symptoms (name, keywords) VALUES
('Headache', 'head ache,head hurts,throbbing head,head pain'),
('Runny Nose', 'nose running,dripping nose,nasal discharge,rhinorrhea'),
('Sore Throat', 'throat pain,scratchy throat,soreness in throat,pharyngitis'),
('Blocked Ears', 'clogged ears,ears feel full,muffled hearing,ear pressure,ear popping'),
('Cough', 'coughing,hacking,dry cough,wet cough,chesty cough'),
('Fever', 'high temperature,feverish,hot,temp,temperature'),
('Body Aches', 'muscle aches,body pain,aching muscles,sore muscles'),
('Fatigue', 'tired,exhausted,weary,low energy,malaise'),
('Sneezing', 'sneezes,sneezy'),
('Nasal Congestion', 'stuffy nose,blocked nose,nasal blockage,congestion'),
('Chills', 'shivering,feeling cold,cold shivers'),
('Loss of Appetite', 'no appetite,don''t want to eat,loss of hunger'),
('Vomiting', 'throwing up,puking,sick to stomach'),
('Diarrhea', 'loose stools,runny poop'),
('Nausea', 'sick feeling,upset stomach'),
('Difficulty Swallowing', 'pain swallowing,sore throat swallowing'),
('Swollen Lymph Nodes', 'swollen glands,neck lumps'),
('White Patches on Tonsils', 'white spots throat,tonsil patches');

-- Link Diseases to Symptoms
INSERT INTO disease_symptoms (disease_id, symptom_id, weight) VALUES
-- Common Cold
((SELECT id FROM diseases WHERE name = 'Common Cold'), (SELECT id FROM symptoms WHERE name = 'Runny Nose'), 1.0),
((SELECT id FROM diseases WHERE name = 'Common Cold'), (SELECT id FROM symptoms WHERE name = 'Sore Throat'), 0.8),
((SELECT id FROM diseases WHERE name = 'Common Cold'), (SELECT id FROM symptoms WHERE name = 'Cough'), 0.7),
((SELECT id FROM diseases WHERE name = 'Common Cold'), (SELECT id FROM symptoms WHERE name = 'Nasal Congestion'), 0.9),
((SELECT id FROM diseases WHERE name = 'Common Cold'), (SELECT id FROM symptoms WHERE name = 'Sneezing'), 0.9),
((SELECT id FROM diseases WHERE name = 'Common Cold'), (SELECT id FROM symptoms WHERE name = 'Headache'), 0.5),
((SELECT id FROM diseases WHERE name = 'Common Cold'), (SELECT id FROM symptoms WHERE name = 'Fatigue'), 0.6),

-- Influenza (Flu)
((SELECT id FROM diseases WHERE name = 'Influenza (Flu)'), (SELECT id FROM symptoms WHERE name = 'Fever'), 1.0),
((SELECT id FROM diseases WHERE name = 'Influenza (Flu)'), (SELECT id FROM symptoms WHERE name = 'Cough'), 0.9),
((SELECT id FROM diseases WHERE name = 'Influenza (Flu)'), (SELECT id FROM symptoms WHERE name = 'Sore Throat'), 0.8),
((SELECT id FROM diseases WHERE name = 'Influenza (Flu)'), (SELECT id FROM symptoms WHERE name = 'Body Aches'), 1.0),
((SELECT id FROM diseases WHERE name = 'Influenza (Flu)'), (SELECT id FROM symptoms WHERE name = 'Fatigue'), 0.9),
((SELECT id FROM diseases WHERE name = 'Influenza (Flu)'), (SELECT id FROM symptoms WHERE name = 'Headache'), 0.8),
((SELECT id FROM diseases WHERE name = 'Influenza (Flu)'), (SELECT id FROM symptoms WHERE name = 'Chills'), 0.7),
((SELECT id FROM diseases WHERE name = 'Influenza (Flu)'), (SELECT id FROM symptoms WHERE name = 'Runny Nose'), 0.6),
((SELECT id FROM diseases WHERE name = 'Influenza (Flu)'), (SELECT id FROM symptoms WHERE name = 'Nasal Congestion'), 0.6),

-- Allergies
((SELECT id FROM diseases WHERE name = 'Allergies'), (SELECT id FROM symptoms WHERE name = 'Sneezing'), 1.0),
((SELECT id FROM diseases WHERE name = 'Allergies'), (SELECT id FROM symptoms WHERE name = 'Runny Nose'), 0.9),
((SELECT id FROM diseases WHERE name = 'Allergies'), (SELECT id FROM symptoms WHERE name = 'Nasal Congestion'), 0.8),
((SELECT id FROM diseases WHERE name = 'Allergies'), (SELECT id FROM symptoms WHERE name = 'Cough'), 0.5),
((SELECT id FROM diseases WHERE name = 'Allergies'), (SELECT id FROM symptoms WHERE name = 'Blocked Ears'), 0.6),

-- Headache (Tension)
((SELECT id FROM diseases WHERE name = 'Headache (Tension)'), (SELECT id FROM symptoms WHERE name = 'Headache'), 1.0),
((SELECT id FROM diseases WHERE name = 'Headache (Tension)'), (SELECT id FROM symptoms WHERE name = 'Fatigue'), 0.4),

-- Strep Throat
((SELECT id FROM diseases WHERE name = 'Strep Throat'), (SELECT id FROM symptoms WHERE name = 'Sore Throat'), 1.0),
((SELECT id FROM diseases WHERE name = 'Strep Throat'), (SELECT id FROM symptoms WHERE name = 'Fever'), 0.9),
((SELECT id FROM diseases WHERE name = 'Strep Throat'), (SELECT id FROM symptoms WHERE name = 'Difficulty Swallowing'), 0.9),
((SELECT id FROM diseases WHERE name = 'Strep Throat'), (SELECT id FROM symptoms WHERE name = 'Swollen Lymph Nodes'), 0.8),
((SELECT id FROM diseases WHERE name = 'Strep Throat'), (SELECT id FROM symptoms WHERE name = 'White Patches on Tonsils'), 1.0),
((SELECT id FROM diseases WHERE name = 'Strep Throat'), (SELECT id FROM symptoms WHERE name = 'Headache'), 0.6),
((SELECT id FROM diseases WHERE name = 'Strep Throat'), (SELECT id FROM symptoms WHERE name = 'Nausea'), 0.5),
((SELECT id FROM diseases WHERE name = 'Strep Throat'), (SELECT id FROM symptoms WHERE name = 'Vomiting'), 0.5),
((SELECT id FROM diseases WHERE name = 'Strep Throat'), (SELECT id FROM symptoms WHERE name = 'Loss of Appetite'), 0.4);

-- Initial Suggestions Data
INSERT INTO suggestions (text, disease_id, is_general_advice) VALUES
-- General Advice
('Please consult a medical professional for a proper diagnosis and treatment plan, especially if your symptoms worsen or persist.', NULL, TRUE),
('It''s always best to consult a doctor if you are unsure about your symptoms or if they are severe.', NULL, TRUE),
('Stay hydrated by drinking plenty of water and clear fluids.', NULL, TRUE),
('Get plenty of rest to help your body recover.', NULL, TRUE),
('Maintain a balanced diet with nutrient-rich foods.', NULL, TRUE),
('Wash your hands frequently to prevent the spread of germs.', NULL, TRUE),
('Avoid close contact with others if you are feeling unwell.', NULL, TRUE),

-- Common Cold Specific Suggestions
('For a common cold, over-the-counter pain relievers like ibuprofen or acetaminophen can help with body aches and fever.', (SELECT id FROM diseases WHERE name = 'Common Cold'), FALSE),
('Try using saline nasal sprays or a neti pot to relieve nasal congestion.', (SELECT id FROM diseases WHERE name = 'Common Cold'), FALSE),
('Sore throat lozenges or sprays can provide temporary relief for a common cold.', (SELECT id FROM diseases WHERE name = 'Common Cold'), FALSE),

-- Influenza (Flu) Specific Suggestions
('For the flu, rest is crucial. Avoid strenuous activities.', (SELECT id FROM diseases WHERE name = 'Influenza (Flu)'), FALSE),
('Antiviral medications might be prescribed by a doctor for the flu, especially if taken early.', (SELECT id FROM diseases WHERE name = 'Influenza (Flu)'), FALSE),
('Flu shots are recommended annually to prevent influenza or reduce its severity.', (SELECT id FROM diseases WHERE name = 'Influenza (Flu)'), FALSE),

-- Allergies Specific Suggestions
('For allergies, try to identify and avoid your triggers.', (SELECT id FROM diseases WHERE name = 'Allergies'), FALSE),
('Over-the-counter antihistamines can help relieve allergy symptoms like sneezing and runny nose.', (SELECT id FROM diseases WHERE name = 'Allergies'), FALSE),
('Nasal corticosteroid sprays can be effective for managing nasal congestion from allergies.', (SELECT id FROM diseases WHERE name = 'Allergies'), FALSE),

-- Headache (Tension) Specific Suggestions
('For tension headaches, try stress-reduction techniques like meditation, yoga, or deep breathing exercises.', (SELECT id FROM diseases WHERE name = 'Headache (Tension)'), FALSE),
('Over-the-counter pain relievers such as aspirin, ibuprofen, or acetaminophen can help alleviate tension headache pain.', (SELECT id FROM diseases WHERE name = 'Headache (Tension)'), FALSE),
('Applying a warm or cold compress to your head or neck might provide relief for tension headaches.', (SELECT id FROM diseases WHERE name = 'Headache (Tension)'), FALSE),

-- Strep Throat Specific Suggestions
('If you suspect strep throat, it is crucial to see a doctor for testing and antibiotics.', (SELECT id FROM diseases WHERE name = 'Strep Throat'), FALSE),
('Complete the full course of antibiotics prescribed by your doctor for strep throat, even if you feel better.', (SELECT id FROM diseases WHERE name = 'Strep Throat'), FALSE),
('Sore throat relief can be found by gargling with warm salt water.', (SELECT id FROM diseases WHERE name = 'Strep Throat'), FALSE);