""""""

# grigorebianca76@gmail.com
# xhamanichristian@gmail.com
# andrei12225@outlook.com
# alexhancu49@gmail.com


# input limbaj natural o descriere a unei diagrame de orice fel iar llm ul sa produca diagrama ,
# o sa existe typo uri, neclaritati in query si aplicatia trebuie sa acopere cazul asta
# bonus pt elem inovative in aplicatie
# https://www.eraser.io
# componenta care tine istoricul conversatiei
# diagrama trebuie sa fie editabila!!!
# corectitudine logica, acuratete tehnica


# https://www.eraser.io/ai/azure-diagram-generator
# diagrama sa fie conforme promptului
# input: prompt in limbaj natural, NU se modifica manual
#       - putem folosi un agent specializat pe limbaj natural pentru a corecta greselile gramaticale
#
# submisie:
# un email cu link catre repo si ss-uri/video-uri cu functionalitatea aplicatiei,
# inclusiv raspunsurile la prompt=urile date de ei
#       + putem demosntra chestiile extra prin ss-uri/video-uri extra


# Cea mai eficientă structură este: 2 pe Frontend/Vizual, 2 pe AI/NLP, 1 pe Backend/Arhitectură și 1 pe Produs/QA/Demo.

# 1. Dev 1: Specialist Frontend (Diagram Engine) - Rolul Critic
# Responsabilitate: Să facă diagrama editabilă. Acesta este cel mai greu punct.

# Task-uri: * Integrează o librărie de diagrame (ex: React Flow / xyflow, Excalidraw SDK, sau Mermaid.js cu un split-pane text-to-visual).

# Scrie logica care transformă output-ul structurat al LLM-ului (ex: un JSON sau sintaxă Mermaid) în noduri și muchii pe care utilizatorul le poate muta, șterge sau redenumi manual pe canvas.

# Se asigură că actualizările vizuale se sincronizează înapoi în starea aplicației.

# 2. Dev 2: Specialist Frontend (UI/UX & Istoric)
# Responsabilitate: Interfața aplicației (partea stângă/dreaptă din Eraser.io).

# Task-uri: * Construiește componenta de chat (input-ul de limbaj natural).

# Implementează componenta de istoric al conversației (UI-ul pentru a naviga prin versiunile anterioare ale diagramei sau prin discuții).

# Se asigură că aplicația arată impecabil pentru capturile de ecran (ss-uri) și video-ul final.

# 3. Dev 3: Arhitect AI / Pipeline Multi-Agent
# Responsabilitate: Inima aplicației - transformarea textului impur în structuri logice.

# Task-uri: * Implementează agentul de corectare (Pre-processing): Un apel LLM rapid (sau un model mai mic, mai ieftin) care preia promptul utilizatorului, corectează typo-urile, rezolvă neclaritățile și reformulează intenția.

# Implementează agentul de generare: Ia textul curățat și generează structura diagramei (JSON/Mermaid), asigurând corectitudinea logică.

# 4. Dev 4: Prompt Engineer & Tester Acuratețe
# Responsabilitate: Calitatea output-ului și rezolvarea cazurilor de test ale juriului.

# Task-uri: * Se concentrează 100% pe a face diagramele să fie conforme promptului.

# Rulează prompturile "date de ei" (cazurile oficiale de testare) la infinit, ajustează System Prompts (ex: "You are an expert cloud architect. Generate an accurate Azure architecture...") până când rezultatul este perfect.

# Se asigură de acuratețea tehnică (ex: ca o bază de date să nu fie conectată ilogic la un load balancer).

# 5. Dev 5: Backend & Integrare (The "Glue")
# Responsabilitate: Să lege frontend-ul de AI și să gestioneze baza de date.

# Task-uri: * Creează API-urile pentru frontend.

# Gestionează baza de date pentru istoricul conversației (ex: Supabase, Firebase sau chiar un simplu SQLite local/în memorie dacă e un hackathon rapid).

# Gestionează contextul conversației pentru LLM (trimite ultimele X mesaje către AI pentru a menține contextul editărilor).

# 6. Product Owner, QA, Demo & "Bonusuri" (Alex? 😉)
# Responsabilitate: Submisia finală, punctele bonus și coordonarea.

# Task-uri: * Inovație (Bonus): Se gândește și implementează quick-wins pentru puncte extra (ex: Input vocal cu un API de Speech-to-Text, export automat în PDF/PNG, generare de cod Terraform direct din diagrama creată).

# QA: Testează la sânge aplicația: "Ce se întâmplă dacă scriu complet greșit?", "Ce se întâmplă dacă cer să editeze doar culoarea unui nod?".
