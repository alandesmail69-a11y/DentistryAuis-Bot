import os, io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from google import genai
import PyPDF2

# ---------- COURSES AND LECTURES ----------
LECTURES = {
    "1": {
        "name": "Semester 1",
        "courses": {
            "ethics": {
                "name": "Ethics",
                "lectures": {
                    "1":  "Lecture 1: Introduction to Dental Ethics",
                    "2":  "Lecture 2: Principal Features of Dental Ethics",
                    "3":  "Lecture 3: Ethical Relationship in the Dentist–Patient Interaction",
                    "4":  "Lecture 4: Dentists and Society",
                    "5":  "Lecture 5: Dentist and Colleagues / Employee Relationship Rights",
                    "6":  "Lecture 6: Confidentiality and Patients Records",
                    "7":  "Lecture 7: Legal Regulation in Dentistry",
                    "8":  "Lecture 8: Business Ethics in Dentistry",
                    "9":  "Lecture 9: Informed Consent",
                    "10": "Lecture 10: Ethical Considerations in Pediatric Dentistry",
                    "11": "Lecture 11: Negligence and Litigation in Dentistry",
                    "12": "Lecture 12: Substituted Consent for Dental Care Decisions",
                    "13": "Lecture 13: Medical & Dental Research Ethics",
                }
            },
            "terminology": {
                "name": "Terminology",
                "lectures": {}
            },
            "biology": {
                "name": "Biology",
                "lectures": {}
            },
        }
    },
    "2":  {"name": "Semester 2",  "courses": {}},
    "3":  {"name": "Semester 3",  "courses": {}},
    "4":  {"name": "Semester 4",  "courses": {}},
    "5":  {"name": "Semester 5",  "courses": {}},
    "6":  {"name": "Semester 6",  "courses": {}},
    "7":  {"name": "Semester 7",  "courses": {}},
    "8":  {"name": "Semester 8",  "courses": {}},
    "9":  {"name": "Semester 9",  "courses": {}},
    "10": {"name": "Semester 10", "courses": {}},
    "11": {"name": "Semester 11", "courses": {}},
}

# Store text per lecture: key = "sem_course_lectureId"
lecture_contents = {
    "1_ethics_1": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 1

What is Ethics:
Ethics comes from the Greek word Ethos, meaning Character or Conduct.
Moral, derived from the Latin word Mores, means Customs or Habits.
The term ethics refers to the study of the concepts of moral right and wrong or moral good and bad.

Why is Ethics Very Important in Dentistry?
Dentists work directly on patients who are often: in pain, anxious or fearful, dependent on professional judgment.
Patients usually cannot judge the quality of dental treatment themselves.
This creates an imbalance of power between the dentist and the patient.

Difference between Ethics and Morals:
Morals are deeply personal and are influenced by various factors like Culture, Religion, and Personal experiences.
Morals guide personal behavior and decision-making which are embedded in emotions and personal beliefs.
Morals tend to be long-standing and resistant to change.
Ethics aims to establish universal standards that go beyond cultural differences.
Ethics manage professional conduct and organizational practices like Codes of Conduct in workplaces.
Ethics evolve over time to address new social, technological, and ethical challenges.

Why is Ethics Very Important in Dentistry?
Dentistry combines: Health care, Technical skill, Business practice.
Ethical decisions are made daily, not only in difficult cases.
It can be done in: Treatment planning, Fees and alternatives, Confidentiality, Informed consent.

How can we know if a decision is ethical?
Ethical decisions are guided by: Professional codes of ethics, National and international dental organizations, Laws and regulations, Personal professional judgment.
Ethics isn't a personal opinion alone.

International Dental Associations and Organizations:
FDI World Dental Federation: Sets guidance for dental practice worldwide and global ethical principles.
National dental associations: They apply and enforce ethical standards within their country according to local laws and regulations.

Importance of Confidentiality:
Patients share sensitive personal and medical information.
Confidentiality builds trust, respects patient dignity, and is both an ethical and legal obligation.
Breaches of confidentiality can harm the patients, lead to legal consequences, and result in loss of professional credibility.

Can the principles of ethics change over time?
Ethical principles are stable, but applications of ethics evolve due to technology, social changes, and new treatment methods.
Such as: Social media use, Digital patient records, Advertising dentistry online.

Discussion case: A dentist has the technical skills to perform an advanced cosmetic procedure, but the treatment is not necessary for the patient's oral health.
""",

    "1_ethics_2": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 2
Principal Features of Dental Ethics

Learning outcomes: Understand what makes dental ethics important in dentistry. Recognize the main ethical principles and professional values in dental practice. Use basic ethical reasoning to discuss simple clinical cases.

Why do we study Dental Ethics?
1. Ethics is part of everyday dentistry
2. Technical skill alone is not enough
3. Ethical conflicts happen during normal treatment

What makes Dentistry Ethically Challenging?
Patients trust dentists with their bodies. Procedures may be painful or irreversible. Information imbalance. Dentistry combines healthcare and business.

Dentists' Dual Role: Patient welfare and Financial sustainability.

Who Makes The Decision, What is Ethical?
A. Personal values, B. Professional codes, C. Law, D. Society and culture, E. Professional organizations.

Core Ethical Principles (ADA Framework):
Autonomy – Respect patient choices
Beneficence – Act for the patient's advantage
Non-maleficence – Do no harm
Justice – Fair treatment
Veracity – Truthfulness

Ethical Principles Compete:
Ethical conflicts happen when principles clash: Autonomy vs beneficence, Justice vs personal preference, Truthfulness vs patient anxiety.

Values to adhere with: 1. Compassion, 2. Competence, 3. Respect, 4. Integrity, 5. Confidentiality.

Confidentiality (Everyday Ethics): Why does it matter? Patient trust, Privacy, Professional responsibility.

Does Ethics Change Over Time?
Principles are stable, but applications can change (Digital records, Social media, Online marketing).

Ethics Across Countries: Culture, Law, Healthcare resources.

Ethical Thinking Steps:
1. Identify the ethical problem, 2. Who is affected?, 3. What principles apply?, 4. What options exist?, 5. Choose and justify a decision.

Cases:
Case 1: Nurse asks to do scaling of colleague's teeth during lunch break.
Case 2: Parent refuses extraction for child with severe decay.
""",

    "1_ethics_3": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 3
Ethical Relationship in the Dentist–Patient Interaction

Learning outcomes: Understand what makes the dentist–patient relationship ethically unique. Recognize professional responsibilities in communication, consent, and trust. Apply ethical principles to common dentist–patient situations.

Why Does This Relationship Matter?
A. Built on trust, B. Information imbalance, C. Patient vulnerability, D. Long-term professional relationship.

What Do Patients Expect?
Good dentist: Manages anxiety, Explains procedures, Shows respect.
Bad Dentist: Poor communication, Disrespect for time or feelings.

Evolution Of The Relationship:
In the past the dentist would decide. Today it is a shared decision-making.

Models of Patient-Dentist Relationship:
1. Guild (Paternalistic) – Dentist decides, patient passive, doctor knows best.
2. Agent – Dentist follows patient requests, patient fully controls decisions.
3. Commercial – Patient is the consumer, the dentist is the service provider, market-driven decisions.
4. Interactive (preferred) – Shared decision-making, dentist is the advisor, patient is an active partner, mutual respect.

Professional Standards: Respect & equal treatment, Communication and consent, Emergency responsibilities, Confidentiality, Financial fairness.

Respect & Equal Treatment: No discrimination, Equal care for all patients, Professional boundaries.

Communication and Consent: Explain procedures clearly, Risks and alternatives, Check understanding, Obtain valid consent.

Confidentiality: Autonomy, Respect, Trust.

Difficult Patients: Fearful children, Non-compliant adults.

Financial Constraints: Ethical options: Payment plans, Referral, Emergency care.

Ethical Challenges in Modern Dentistry:
1. Conflicts of interest, 2. Patient expectations, 3. Cultural differences, 4. Overtreatment risk.

Cases:
Case 1: 16-year-old requests extraction of all wisdom teeth without clinical need.
Case 2: Consent was not fully explained, and a complication happened which led to a complaint. What ethical mistakes happened?

Key takeaway: Ethical relationships require Communication, Empathy, Honesty, Professional boundaries.

Summary:
1. Dentist–patient relationship is trust-based. 2. Interactive model is preferred. 3. Ethics guides communication and decisions. 4. Good relationships prevent legal and ethical problems.
""",

    "1_ethics_4": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 4
Dentists and Society

Learning outcomes: Explain the ethical relationship between dentists and society. Recognize ethical conflicts between individual patient care and social responsibility. Describe dentists' roles in public health and global health.

Why Does Society Matter in Dentistry?
Dentistry is not only individual care: Social responsibility, Public trust, Professional privilege, Community impact.

Professionalism and Society: Service to others, Moral responsibility, Specialized knowledge, Professional autonomy.

Why Society Grants Privileges:
Society allows dentists: Self-regulation, Respect and professional status, Patient trust, Financial independence.
In return: Ethical conduct, Competence, Public protection.

Dentist's Roles in Society: Public health promotion, Health education, Environmental awareness, Legal/forensic roles, Protecting patients from harm.

Dual Loyalty: Dentist Loyalty to 1. Individual Patient, 2. Society.

Examples of Dual Loyalty Conflicts: Dentists may need to report: A. Infectious diseases, B. Child abuse, C. Human rights violations.

Industry and Commercial Conflicts: Dentists must critically evaluate dental products, pharmaceutical claims, manufacturer marketing.

Resource Allocation (limited): Time, Equipment, Money, Workforce.

Levels of Resource Allocations:
Macro level — National decisions, Meso level — Hospital/clinic decisions, Micro level — Dentist decisions.

Ethical Allocation Approaches:
Libertarian – Pay-based access, Utilitarian – Greatest benefit, Egalitarian – Equal need, Restorative – Help disadvantaged.

Dentist Decisions at Micro Level: Radiographs frequency, Treatment complexity, Referral necessity.

Public Health Responsibilities: Educate patients, Promote prevention, Identify social health risks.

Global Health: Cross-border diseases, Shared health challenges, International cooperation (COVID-19, SARS).

Globalization and Dentistry: Migration of dentists, Refugee oral health needs, Workforce imbalance.

FDI recommendations: Prevent exploitation, Support fair recruitment, Maintain workforce balance.

Case: A dentist must report a contagious disease but patient asks for secrecy.

Summary:
1. Dentistry operates under a social contract. 2. Dual loyalty creates ethical challenges. 3. Resource allocation requires fairness. 4. Dentists contribute to public and global health.
""",

    "1_ethics_5": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 5
Dentist and Colleagues / Employee Relationship Rights

Learning outcomes: Describe the ethical responsibilities of dentists toward colleagues and dental staff. Identify unethical behaviors in professional relationships (e.g., fee-splitting, patient attraction). Explain how teamwork and conflict resolution contribute to safe and ethical patient care.

Dentistry is not practiced alone. Dentists work with: Other dentists, Specialists, Dental assistants, Hygienists, Laboratory technicians, Physicians and pharmacists.

Dental Ethics Beyond the Patient: Dental ethics includes duties toward Patients, Colleagues, Society. Ethical behavior must be consistent in all professional relationships.

Core Ethical Principles Applied to Professional Relationships:
Autonomy – Respect professional judgment, Beneficence – Work together for patient benefit, Non-maleficence – Avoid harming patients through ego or competition, Justice – Fair treatment of colleagues, Veracity – Honesty in communication.

Respect Among Dentists: Treat colleagues with dignity, Avoid public criticism, Communicate professionally, Focus on patient welfare.
Professional disagreement is acceptable. Professional disrespect is not.

Referral Ethics:
Refer when: 1. The case exceeds their competence, 2. Specialized skills are required, 3. Patient safety is at risk.
Referral must be based on patient benefit, not financial advantage.

Unethical Referral Practices:
1. Fee-splitting – Receiving money for referring patients; Violates justice and beneficence.
2. Attracting patients from colleagues – Undermining another dentist; Using negative comments to gain patients.

Managing Previous Faulty Treatment: Avoid harsh criticism, Do not speculate, Focus on current patient care, Explain objectively.

Dentist and Employee Relationship: The dentist is the leader, legally responsible, responsible for supervision. Staff must work within their scope.

Scope of Practice of Dental Assistants: Cannot diagnose, cannot establish fees, cannot judge treatment quality. Must follow the dentist's supervision.

Teamwork in Dentistry: Communication, Defined responsibilities, Mutual respect, Shared goal: best patient care.
Poor teamwork increases the risk of errors.

Leadership Responsibility: Maintain a safe environment, Ensure equipment readiness, Supervise infection control, Take ultimate responsibility.

Self-Regulation of Dentistry: Society grants Trust, Privileges, Autonomy. In return, the profession must maintain high ethical standards.

Reporting Unsafe or Unethical Behavior: Recognize unsafe practices, Avoid silent complicity, Follow institutional reporting procedures. Protecting patients is more important than protecting colleagues.

Conflict Resolution: Understand communication styles, Focus on the issue not the person, Address problems early, Be patient and professional.

ADA Code Principles: No fee-splitting (Justice & Beneficence), No false advertising (Veracity), Refer when beyond competence (Non-maleficence), Maintain confidentiality (Autonomy & Respect).

Summary: Respect colleagues, Refer appropriately, Avoid financial conflicts, Supervise staff responsibly, Promote teamwork, Maintain professional integrity.
""",

    "1_ethics_6": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 6
Confidentiality and Patients Records

Learning outcomes: Explain the ethical importance of patient confidentiality in dental practice. Describe the types of information included in dental records and how they must be protected. Identify situations where confidentiality may ethically or legally be breached.

What Are Dental Records?
Dental records contain: Patient's personal information, Medical history, Diagnostic data, Clinical notes, Radiographs and photos, Dentist–patient communication, Consent documentation.
These records help ensure continuity and quality of care.

Why Are Dental Records Important? Diagnose conditions, Plan treatment, Monitor patient progress, Communicate with other healthcare professionals, Protect dentist legally.

Ethical Duty of Confidentiality: Protect patient information, Use information only for healthcare purposes, Prevent unauthorized access.
Breaching confidentiality can lead to legal consequences.

Patient Rights: Privacy, Control over their personal information, Access their health records, Expect professional confidentiality.

Health Records and Data Protection: Contains information about Physical health, Mental health, Medical conditions. Must be protected by data protection laws.

Data Collectors: A data controller is responsible for managing patient information: Protecting patient data, Determining how data is used, Ensuring confidentiality.

Access to Patient Information: Only by Dentist, Dental assistants, Staff directly involved in treatment.

Confidentiality After Death: Confidentiality continues even after the patient dies.

Securing Patient Information: Locked filing cabinets, Password-protected computer systems, Restricted access to electronic records, Confidential conversations.

Confidentiality in Clinic Design: Prevent conversations from being overheard, Protect patient privacy, Secure patient files.

Social Media and Confidentiality: Dentists must never post patient information online without permission. Even anonymized cases must be carefully protected.

Patient Photos: Obtain written consent, Explain how images will be used, Ensure patient identity protection.

Ethical Basis of Confidentiality: Autonomy, Respect for persons, Trust. Without confidentiality, patients may hide important information.

When Confidentiality May Be Breached: 1. Legal requirements, 2. Protection of others from harm, 3. Mandatory reporting (child abuse).

Dual Loyalty: Responsibilities toward Patient, Society, Government, Employers.

Example: If a patient refuses to inform their partner about HIV risk, disclosure may sometimes be justified to protect others.

Summary: Confidentiality is essential in healthcare. Dental records must be secure. Patient trust depends on privacy. Breaches are allowed only in exceptional situations.
""",

    "1_ethics_7": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 7
Legal Regulation in Dentistry (National and International)

Learning outcomes: Explain why dentistry is regulated by law. Identify the legal responsibilities of dentists in clinical practice. Compare national and international systems that regulate dentistry.

Why Is Dentistry Regulated? Protect patient safety, Ensure qualified professionals provide treatment, Maintain professional standards, Prevent malpractice and negligence.

What Do Legal Regulations Define? Who is allowed to practice dentistry, Required qualifications and licensing, Standards of care, Professional responsibilities, Penalties for misconduct or malpractice.

Importance of Legal Regulation: Protect patients' rights, Maintain public trust in dentistry, Ensure ethical practice, Provide accountability for professional misconduct.

Standards of Care:
National Standard of Care – Dentists are judged according to national professional standards.
Locality Rule – Dentists are evaluated according to standards in their local community.

Authorities That Regulate Dentistry: 1. Ministry of Health, 2. Dental Councils, 3. National Dental Associations.

Legal Responsibilities of Dentists: Obtain informed consent, Maintain accurate patient records, Follow infection control standards, Avoid negligence or malpractice, Protect patient confidentiality.

Common Legal Issues in Dentistry: Misdiagnosis or treatment error, Lack of informed consent, Breach of confidentiality, Failure to refer complex cases, False advertising or unlicensed practice.

International Regulation: WHO – promotes global oral health policies, FDI World Dental Federation – develops ethical guidelines, International dental organizations – encourage professional standards.

National vs International Regulation:
National: Government or dental council authority, country-specific scope, controls dental practice.
International: Global organizations, worldwide standards, promotes global quality.

Cultural Practices and Dental Ethics: Grinding front teeth for aesthetics, Removing certain teeth for cultural identity. These practices illustrate how cultural traditions may conflict with modern dental ethics.

Acceptable Tooth Extraction: Orthodontic treatment, Correcting severe malocclusion.

Regulation of Dentistry in Kurdistan Region: Kurdistan Dental Association (KDA), Dentists Syndicate Law (2004), Dentists must be members of the KDA to practice legally.

Regulation in Iraq: Iraq Dental Association oversees licensing and professional regulation.

Regulation in the United States: American Dental Association (ADA), Commission on Dental Accreditation (CODA), Regional dental licensing boards.

Regulation in Canada: National Dental Examining Board of Canada (NDEB), Commission on Dental Accreditation of Canada, Royal College of Dentists of Canada.

Key Points: Dentistry is regulated by law to protect patients. Dentists must follow legal and ethical standards. National and international organizations guide dental practice.
""",

    "1_ethics_8": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 8
Business Ethics in Dentistry

Learning outcomes: Explain how business pressures influence ethical decision-making in dentistry. Identify unethical practices in advertising, treatment planning, and financial decisions. Apply ethical principles to conflicts between patient care and business interests.

Dentistry as a Profession and a Business: Patients pay for treatment. Dentists earn income. Ethical duties must still be followed.

Professional vs Business Ethics:
Professional Ethics: Patient-centered, Focus on care, Ethical duty.
Business Ethics: Profit-driven, Focus on revenue, Financial sustainability.
Problems arise when business decisions override professional ethics.

Conflict of Interest (COI): Occurs when personal or financial interests influence clinical decisions. COI is not always unethical, but it creates risk. Having a conflict is normal — but acting unfairly because of it is unethical.

Personal vs Patient Interest: Choosing faster but poorer treatment, Scheduling based on convenience instead of quality, Selecting profit over best care.

Third-Party Influence: Insurance companies, Employers, Government systems. The dentist must always recommend the best treatment for the patient.

Ethical Advertising: Be truthful, Be evidence-based, Provide information not manipulation.

Unethical Advertising: False claims, Digitally enhanced results, Claiming superiority over other dentists.

Inducements and Discounts: Gifts for patients, Referral rewards, Heavy discounts. Problem: Influences patient decisions unfairly.

Social Media in Dentistry: Avoid misleading before and after images, creating unrealistic expectations, promoting unnecessary treatments.

Competitive Spirit vs Integrity: Competition may lead to Overtreatment, Undermining colleagues, Financial bias.

Aesthetic and Cosmetic Dentistry:
Esthetic Dentistry: Restores function and natural appearance.
Cosmetic Dentistry: Changes appearance beyond normal.

Ethical Issues in Cosmetic Dentistry: Treating healthy teeth unnecessarily, Following trends instead of science, Patient pressure vs professional judgment.

Extending Scope of Practice: Work within competence, Avoid performing unfamiliar procedures, Refer when needed.

New / Unproven Treatments: Use evidence-based treatments, Avoid promoting unproven techniques (e.g., unnecessary frenectomy in infants).

Unscientific Treatments: Rejecting proven treatments (fluoride, endodontics), Promoting fake or unsupported methods.

Non-Dental Treatments: Botox (outside proper indication), Fillers, tattoos, piercing. These may fall outside dentistry and can be unethical depending on context.

Unacceptable Business Practices: Overtreatment, Undertreatment, Charging for services not done, Overcharging or undercharging, Cutting corners.

Summary: Dentistry is both business and profession. Ethics must guide financial decisions. Avoid conflicts of interest. Use evidence-based practice. Protect patient trust.
""",

    "1_ethics_9": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 9
Informed Consent

Learning outcomes: Explain the concept and components of informed consent. Identify different types of consent and decision-making situations. Understand how justice influences access to dental care and resource distribution.

An Informed Consent: A process of communication between dentist and patient that allows the patient to make a decision.
It is: a legal requirement, an ethical duty, part of patient autonomy.

Why is it important? Respects patient autonomy, Builds trust, Protects dentist legally, Improves decision-making.

What Should be Explained? Diagnosis, Treatment options (including no treatment), Risks and benefits, Costs, Alternatives.

The Components of a Valid Consent:
A. Information – sufficient explanation should be provided
B. Capacity – the patient can decide on their treatment
C. Voluntary – no pressure should be applied on the patient

Types of Consent: Verbal consent, Written consent, Implied consent, Explicit consent, Presumed consent.

Verbal and Written Consent:
Verbal: simple, low-risk procedures.
Written: surgical or high-risk procedures.

Implied vs Explicit Consent:
Implied: patient behavior (sitting in a chair).
Explicit: direct agreement for a treatment.

Presumed Consent (Emergencies): Patient is unconscious, immediate treatment is needed.

Consent in Children & Incompetent Patients: Decisions made by parents. Replacement (someone else) may decide for adults. Emergency leads to presumed consent.

Substitute Decision Making:
A. Substituted judgment – what the patient would want
B. Best interest – what is best for the patient

Social Justice in Dentistry: Fair distribution of healthcare, Equal respect for all patients, Access to care.

Basic Needs and Distribution of Care: Consider Urgency, Need, Fairness.

Contribution and Effort: Some systems consider patient's role in their healthcare. The main ethical concern: May be unfair or discriminatory to judge their habits.

Free Market View: Healthcare based on ability to pay. Problem: Inequality in access.

Basic Dental Care Concept: Everyone should be able to have Emergency care, Pain relief, Basic treatment. This is the minimum ethical standard.

Summary: Informed consent is communication and understanding. Valid consent requires 3 elements. Different types of consent exist. Justice ensures fairness in care.
""",

    "1_ethics_10": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 10
Ethical Considerations in Pediatric Dentistry

Learning outcomes: Understand ethical challenges in treating children. Explain informed consent in pediatric dentistry. Balance autonomy, beneficence, and parental influence. Analyze ethical dilemmas in pediatric cases.

Why do we consider Pediatric Dentistry to be different? Children are still developing, Limited ability to decide, They depend on their parents, There are emotional and psychological factors.

If treatment is essential, parents and dentists prioritize the child's benefit. A child's autonomy is different from an adult's, so communication is important. The dentist should explain treatment in a simple, age-appropriate way to involve the child and make them feel safe.

Triangle in Pediatric Dentistry: Three entities are involved: 1. Dentist, 2. Parent, 3. Child.
Decisions are not made by one person; they involve all three.

Ethical Principles: Autonomy, Beneficence, Non-maleficence, Justice.

Communication with Children: Use simple language, Consider age and development, Make the child feel safe.

Informed Consent in Children: The parents will give legal consent for the child. The child should still be involved.

Child Assent: The child should agree to the treatment, even if not legally required.

Balancing Autonomy and Beneficence: Problem: Child refuses treatment but treatment is needed. This creates a conflict between respecting autonomy and doing what is best for the child.

Integrity (Dignity): Respecting the child as a person, Not ignoring the child's feelings, Not focusing only on the parents.

Autonomy in Children: Not fully developed autonomy, Their autonomy grows with age, Their autonomy must be respected gradually.

Role of the Parents: Give consent, Act in the child's best interest. BUT: They may have conflicts due to fear, time, stress.

Dentist as Child Advocate: Protect the child's best interest, Question harmful decisions, Balance parent and child needs. A dentist's duty is to the child first.

When Principles Conflict: Child refuses treatment but treatment is beneficial. Conflict: Autonomy vs Beneficence.

When to Postpone Treatment: If it's not urgent, If the child is very anxious, If better cooperation will be achieved later.

When Immediate Treatment is Needed: Trauma (avulsion) happens, Infection is present. In emergencies, beneficence may override autonomy.

Pain Control & Behavior Management: Reduce pain, Use behavior techniques, Consider sedation if needed. Reduction of suffering is an ethical treatment.

Child Neglect and Abuse: The dentist must have the skills to recognize signs and report appropriately.

Summary: Pediatric ethics is complex. Child plus parent plus dentist interaction. Balancing autonomy and beneficence. Always act in child's best interest.
""",

    "1_ethics_11": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 11
Negligence and Litigation in Dentistry

Learning outcomes: Define negligence clearly. Identify its key elements. Recognize legal risks in dental practice. Understand how to prevent litigation.

When ethical practice fails, legal consequences follow. Complaints may lead to legal cases. Early communication can prevent litigation.

Negligence: Failure to provide the standard of care expected from a dentist, resulting in harm to the patient.
Not every mistake is negligence. Harm must be present.

Examples of Negligence: Not diagnosing caries, Wrong extraction, Ignoring infection. All of these points will lead to patient harm.

Elements of Negligence:
1. Duty of care, 2. Breach of duty, 3. Causation, 4. Damage.

Duty of Care: Dentist–patient relationship exists. Dentist must provide proper care.

Breach of Duty: The care provided falls below the standard of care.
Examples: Wrong diagnosis, Poor technique, No consent.

Standard of Care: Based on average skilled dentist. Higher skill expected for complex procedures.
If you do implants, you are judged as an implant dentist — not a beginner.

Causation: Your action must cause the harm.

Damage (Injury): Physical, Psychological, Financial. If there is no injury, there is no case.

Non-Negligent Situations: Known complications, Proper consent taken, Patient non-compliance.
A bad outcome does not mean the dentist is wrong.

Liability of Dentist: Their work, Staff actions.

Breach of Contract: In private treatment, a patient can complain if the result does not meet the agreed standard. The patient does not need to prove negligence, only that the treatment was not satisfactory. Treatment should be safe, functional, and of good quality. If it is not, the patient can reject the treatment and claim compensation.

Compensation: Financial payment only (the only remedy for injury in civil claims is money).
Types: A. General (pain), B. Special (costs).
Examples: Pain and suffering, Treatment costs, Future care.

Legal Process: 1. Complaint, 2. Investigation, 3. Expert review, 4. Court.
Patients usually use a specialized lawyer. Dentists are supported by a defense organization.

Prevention: Good communication, Proper consent, Documentation, Follow standards.
Most lawsuits are prevented by communication, not skill.

Summary: Negligence is a combination of breach and harm. It requires 4 elements. Not all outcomes are negligence. Prevention is key.
""",

    "1_ethics_12": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 12
Substituted Consent for Dental Care Decisions

Learning outcomes: Define substituted consent and when it is used. Identify patients with compromised decision-making capacity. Understand the role of parents and legal guardians. Apply ethical reasoning to clinical cases.

Substituted Consent: Consent given by another person on the patient's behalf.
Used when the patient: Can't understand, Can't decide, Can't communicate.

Capacity to Decide: Capacity is the ability to: Understand information, Evaluate options, Make a decision, Communicate choice.

Who doesn't have the Capacity to decide? Children, Unconscious patients, Patients with mental disability, Severe illness or confusion.

Substituted Decision Makers: Parents, Legal guardians, Court-appointed decision makers.

Types of Substituted Consent:
1. Implied Consent – Shown by the patient's actions (sitting in a chair, opening the mouth); only for examination.
2. Verbal Consent – Spoken agreement; used for simple, low-risk procedures (scaling, simple filling).
3. Written Consent – Signed document; required for surgical/high-risk procedures (extraction, implants).
4. Explicit Consent – Clear, informed agreement (verbal or written); required for treatment plans.
5. Presumed Consent – Used in emergencies when the patient is unable to respond.

Role of Parents & Guardians: Act in the child's best interest, Make informed decisions, Consider long-term outcomes.

The Responsibility of The Dentist: Protect patient welfare. Do not blindly follow parents' decisions. Act as patient advocate.

Substituted Judgment: What would the patient choose? Used when patient previously expressed wishes.

Best Interest Standard: What is the best medical treatment for the patient? Used when patient preferences are unknown.

The capacity of a Patient: Full capacity, Partial capacity, No capacity. Most patients are in the middle, where ethics becomes difficult.

Partial Capacity: Elderly patient with mild dementia, Anxious or confused patient, A child who understands partially. These patients should still be involved in decisions.

Managing Partial Capacity Patients: Simplifying information, Check their understanding, Involve the patient and guardians, Respect the patient as much as possible.

Ethical Conflicts: Patient refuses treatment, Guardian agrees, Dentist sees benefit.

Decision-Making in Ethical Conflicts: Consider Patient's wishes, Medical benefit, Risk of harm, Urgency.

When to Override Refusal: Serious harm is expected, Patient lacks capacity, Treatment is urgent.

Assignment: An elderly patient with confusion refuses treatment, but family members agree.
1. Does the patient have full decision-making capacity?
2. Who should make the final decision?
3. Which ethical principles are involved?
4. What is the most appropriate action for the dentist?

Summary: Capacity determines consent. Substituted consent is common. Parents/guardians play key role. Patient must still be involved. Dentist protects patient interest.
""",

    "1_ethics_13": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 13
Medical & Dental Research Ethics

Learning outcomes: Understand why research is important in dentistry. Identify ethical requirements in research. Explain risks, benefits, and consent in research. Recognize unethical research behavior.

Why do we have ethics in research? In the past, research was done without consent and patients were harmed.

Nuremberg Code (1949):
1. Voluntary informed consent is essential.
2. Human research has to be based on prior animal experiments.
3. Justification of benefit to individuals and society.
4. No expectation of physical and mental suffering and injury.
5. No expectation of death/injury from an experiment.
6. The risk should not exceed the benefits.
7. Proper preparations to protect the experimental subject.
8. Scientifically qualified persons should experiment.
9. Human subjects must have the freedom to end the experiment.
10. Scientists must be ready to stop the experiment at any point if continuing could cause injury, disability, or death.

Belmont Report: Defines 3 main principles: A. Respect for persons, B. Beneficence, C. Justice.

Declaration of Helsinki: The World Medical Association (WMA) developed this as a statement of ethical principles for medical research involving human participants.

Importance of Research: Improves treatments, Develops new materials, Enhances patient care.

Research in Dental Practices: Evidence-based dentistry, Better decision-making, Improved outcomes.

Ethical Requirements: Research must include Ethical approval, Scientific validity, Social value.

Ethics Committee Approval: Research must be approved before starting.

Scientific Merit: Research must be well-designed and based on evidence.

Social Value: Research should benefit society.

Risk and Benefits: Risks must be minimized. Benefits must be greater.

Informed Consent in Research: The purpose of the study, The risks involved, The benefits (if any), The right to withdraw at any time.

Confidentiality: Patient data must be protected. No unauthorized sharing.

Conflict of Roles: Dentist and researcher. Main issue: Patient trust against research goals.

Honest Reporting: Report results honestly. Do not hide negative results.

Whistle Blowing: Reporting unethical research.

Issues Faced: Funding problems, Technology limitations, Diverse populations.

Assignment: A dentist conducts research on patients but does not fully explain risks.
A. Is this ethical?
B. What is missing, and what ethical principles were violated?
C. What is the ideal way for the researcher/dentist to act?
""",
}

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not TOKEN or not GEMINI_KEY:
    print("❌ Missing TELEGRAM_BOT_TOKEN or GEMINI_KEY in Secrets!")
    exit(1)

client = genai.Client(api_key=GEMINI_KEY)


# ---------- LOAD PDFs FROM DISK (for future courses with uploaded PDFs) ----------
def load_pdfs():
    for sem_id, sem_data in LECTURES.items():
        for course_id, course_data in sem_data.get("courses", {}).items():
            for lec_id, lec_name in course_data.get("lectures", {}).items():
                key = f"{sem_id}_{course_id}_{lec_id}"
                if key in lecture_contents:
                    continue  # already pre-loaded (e.g., ethics)
                file_name = f"telegram-bot/pdfs/{sem_id}_{course_id}_{lec_id}.pdf"
                if os.path.exists(file_name):
                    try:
                        with open(file_name, "rb") as f:
                            reader = PyPDF2.PdfReader(f)
                            text = ""
                            for page in reader.pages:
                                text += page.extract_text()
                        if text.strip():
                            lecture_contents[key] = text
                            print(f"✅ Loaded {file_name}")
                    except Exception as e:
                        print(f"⚠️ Error reading {file_name}: {e}")

load_pdfs()


# ---------- BOT FUNCTIONS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(f"📚 {LECTURES[s]['name']}", callback_data=f"sem_{s}")] for s in LECTURES]
    text = "🦷 Welcome! Choose a semester:"
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ---------- SEMESTER SELECTED ----------
    if data.startswith("sem_"):
        sem_id = data[len("sem_"):]
        context.user_data["sem"] = sem_id
        courses = LECTURES[sem_id].get("courses", {})

        if not courses:
            await query.edit_message_text(f"📂 {LECTURES[sem_id]['name']}\n\n⚠️ No courses added yet.")
            return

        keyboard = []
        for course_id, course_data in courses.items():
            name = course_data.get("name", course_id)
            lectures = course_data.get("lectures", {})
            loaded = sum(1 for lec_id in lectures if f"{sem_id}_{course_id}_{lec_id}" in lecture_contents)
            total = len(lectures)
            status = "✅" if loaded == total and total > 0 else f"📤 {loaded}/{total}" if total > 0 else "📤"
            keyboard.append([InlineKeyboardButton(f"{status} {name}", callback_data=f"course_{sem_id}_{course_id}")])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
        await query.edit_message_text(
            f"📂 {LECTURES[sem_id]['name']} - Choose a course:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ---------- COURSE SELECTED ----------
    elif data.startswith("course_"):
        rest = data[len("course_"):]
        sem_id, course_id = rest.split("_", 1)
        course_data = LECTURES[sem_id]["courses"][course_id]
        course_name = course_data.get("name", course_id)
        context.user_data["sem"] = sem_id
        context.user_data["course"] = course_id

        lectures = course_data.get("lectures", {})
        if not lectures:
            await query.edit_message_text(
                f"📂 *{course_name}*\n\n⚠️ No lectures added yet.",
                parse_mode="Markdown"
            )
            return

        keyboard = []
        for lec_id, lec_name in lectures.items():
            key = f"{sem_id}_{course_id}_{lec_id}"
            status = "✅" if key in lecture_contents else "📤"
            keyboard.append([InlineKeyboardButton(
                f"{status} {lec_name}",
                callback_data=f"lec_{sem_id}_{course_id}_{lec_id}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 Back to Courses", callback_data=f"sem_{sem_id}")])
        await query.edit_message_text(
            f"📚 *{course_name}* — Choose a lecture:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ---------- LECTURE SELECTED ----------
    elif data.startswith("lec_"):
        rest = data[len("lec_"):]
        parts = rest.split("_", 2)   # sem_id, course_id, lec_id
        sem_id, course_id, lec_id = parts[0], parts[1], parts[2]
        key = f"{sem_id}_{course_id}_{lec_id}"
        course_data = LECTURES[sem_id]["courses"][course_id]
        course_name = course_data["name"]
        lec_name = course_data["lectures"].get(lec_id, f"Lecture {lec_id}")
        context.user_data["current_lecture"] = key

        if key in lecture_contents:
            keyboard = [
                [InlineKeyboardButton("❓ Ask Question", callback_data=f"ask_{key}")],
                [InlineKeyboardButton("📝 Generate Quiz", callback_data=f"quiz_{key}")],
                [InlineKeyboardButton("🔙 Back to Lectures", callback_data=f"course_{sem_id}_{course_id}")]
            ]
            await query.edit_message_text(
                f"✅ *{lec_name}*\n\nWhat would you like to do?",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            context.user_data["awaiting_upload"] = key
            await query.edit_message_text(
                f"📤 *{lec_name}* has no content yet.\n\nPlease **send the PDF file** for this lecture.",
                parse_mode="Markdown"
            )

    # ---------- ASK / QUIZ ----------
    elif data.startswith("ask_") or data.startswith("quiz_"):
        if data.startswith("ask_"):
            key = data[len("ask_"):]
            action = "ask"
            prompt_hint = "✍️ Type your question below."
        else:
            key = data[len("quiz_"):]
            action = "quiz"
            prompt_hint = "✍️ Type 'yes' to generate a 5-question quiz, or type your specific topic."
        context.user_data["current_lecture"] = key
        context.user_data["action"] = action
        await query.edit_message_text(prompt_hint)

    elif data == "back":
        await start(update, context)


# ---------- HANDLE PDF UPLOADS ----------
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get("awaiting_upload")
    if not key:
        await update.message.reply_text("⚠️ Please select a lecture first using /start.")
        return

    file = await update.message.document.get_file()
    pdf_bytes = await file.download_as_bytearray()

    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        if not text.strip():
            await update.message.reply_text("⚠️ Could not read text from this PDF. Try another file.")
            return

        lecture_contents[key] = text
        context.user_data["awaiting_upload"] = None

        parts = key.split("_", 2)
        sem_id, course_id, lec_id = parts[0], parts[1], parts[2]
        lec_name = LECTURES[sem_id]["courses"][course_id]["lectures"].get(lec_id, f"Lecture {lec_id}")
        await update.message.reply_text(
            f"✅ *{lec_name}* uploaded successfully! ({len(text)} characters)\n\n"
            f"Use /start to navigate back and ask questions!",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error reading PDF: {str(e)}")


# ---------- HANDLE QUESTIONS & QUIZZES ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    key = context.user_data.get("current_lecture")
    action = context.user_data.get("action", "ask")

    if not key or key not in lecture_contents:
        await update.message.reply_text("⚠️ Please select a lecture first using the /start menu.")
        return

    lecture_text = lecture_contents[key]
    parts = key.split("_", 2)
    sem_id, course_id, lec_id = parts[0], parts[1], parts[2]
    lec_name = LECTURES[sem_id]["courses"][course_id]["lectures"].get(lec_id, f"Lecture {lec_id}")

    try:
        if action == "quiz":
            prompt = f"""You are a dentistry professor. Based ONLY on this lecture text, generate a 5-question multiple-choice quiz.
Lecture text: {lecture_text}
Student request: {user_text}
Format: List 5 questions with 4 options each (A, B, C, D) and provide the correct answers at the end."""
        else:
            prompt = f"""You are a dentistry professor. Based ONLY on this lecture text, answer the student's question clearly.
Lecture text: {lecture_text}
Student question: {user_text}"""

        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        await update.message.reply_text(
            f"🧑‍🏫 *{lec_name}*\n\n{response.text}",
            parse_mode="Markdown"
        )
        context.user_data["action"] = "ask"
    except Exception as e:
        await update.message.reply_text(f"⚠️ AI error: {str(e)}")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
