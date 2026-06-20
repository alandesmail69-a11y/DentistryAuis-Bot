import os, io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types
import PyPDF2

LECTURES = {
    "1": {
        "name": "Semester 1",
        "topics": {
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
    "2":  {"name": "Semester 2",  "topics": {}},
    "3":  {"name": "Semester 3",  "topics": {}},
    "4":  {"name": "Semester 4",  "topics": {}},
    "5":  {"name": "Semester 5",  "topics": {}},
    "6":  {"name": "Semester 6",  "topics": {}},
    "7":  {"name": "Semester 7",  "topics": {}},
    "8":  {"name": "Semester 8",  "topics": {}},
    "9":  {"name": "Semester 9",  "topics": {}},
    "10": {"name": "Semester 10", "topics": {}},
    "11": {"name": "Semester 11", "topics": {}},
}

lecture_contents = {
    "1_1": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 1

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

    "1_2": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 2
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
A. Personal values
B. Professional codes
C. Law
D. Society and culture
E. Professional organizations

Core Ethical Principles (ADA Framework):
Autonomy – Respect patient choices
Beneficence – Act for the patient's advantage
Non-maleficence – Do no harm
Justice – Fair treatment
Veracity – Truthfulness

Ethical Principles Compete:
Ethical conflicts happen when principles clash: Autonomy vs beneficence, Justice vs personal preference, Truthfulness vs patient anxiety.

Values that we need to adhere with:
1. Compassion
2. Competence
3. Respect
4. Integrity
5. Confidentiality

Confidentiality (Everyday Ethics):
Why does it matter? Patient trust, Privacy, Professional responsibility.

Does Ethics Change Over Time?
Principles are stable, but applications can change (Digital records, Social media, Online marketing).

Ethics Across Countries: Culture, Law, Healthcare resources.

Ethical Thinking Steps:
1. Identify the ethical problem
2. Who is affected?
3. What principles apply?
4. What options exist?
5. Choose and justify a decision

Cases:
Case 1: Nurse asks to do scaling of colleague's teeth during lunch break.
Case 2: Parent refuses extraction for child with severe decay.
""",

    "1_3": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 3
Ethical Relationship in the Dentist–Patient Interaction

Learning outcomes: Understand what makes the dentist–patient relationship ethically unique. Recognize professional responsibilities in communication, consent, and trust. Apply ethical principles to common dentist–patient situations.

Why Does This Relationship Matter?
A. Built on trust
B. Information imbalance
C. Patient vulnerability
D. Long-term professional relationship

What Do Patients Expect?
Good dentist: Manages anxiety, Explains procedures, Shows respect.
Bad Dentist: Poor communication, Disrespect for time or feelings.

Evolution Of The Relationship:
In the past the dentist would decide. Today it is a shared decision-making.

Models of Patient-Dentist Relationship:
1. Guild (Paternalistic) – Dentist decides, patient passive, doctor knows best.
2. Agent – Dentist follows patient requests, patient fully controls decisions.
3. Commercial – Patient is the consumer, the dentist is the service provider, market-driven decisions.
4. Interactive (preferred) – Shared decision-making, the dentist is the advisor, patient is an active partner, mutual respect.

Professional Standards:
Respect & equal treatment, Communication and consent, Emergency responsibilities, Confidentiality, Financial fairness.

Respect & Equal Treatment: No discrimination, Equal care for all patients, Professional boundaries.

Communication and Consent: Explain procedures clearly, Risks and alternatives, Check understanding, Obtain valid consent.

Confidentiality: Why does it matter? Autonomy, Respect, Trust.

Difficult Patients: Fearful children, Non-compliant adults.

Financial Constraints:
Dentistry cannot be free for everyone. Ethical options: Payment plans, Referral, Emergency care.

Ethical Challenges in Modern Dentistry:
1. Conflicts of interest
2. Patient expectations
3. Cultural differences
4. Overtreatment risk

Cases:
Case 1: 16-year-old requests extraction of all wisdom teeth without clinical need.
Case 2: Consent was not fully explained, and a complication happened which led to a complaint. What ethical mistakes happened?

Key takeaway: Ethical relationships require Communication, Empathy, Honesty, Professional boundaries.

Summary:
1. Dentist–patient relationship is trust-based.
2. Interactive model is preferred.
3. Ethics guides communication and decisions.
4. Good relationships prevent legal and ethical problems.
""",

    "1_4": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 4
Dentists and Society

Learning outcomes: Explain the ethical relationship between dentists and society. Recognize ethical conflicts between individual patient care and social responsibility. Describe dentists' roles in public health and global health.

Why Does Society Matter in Dentistry?
Dentistry is not only individual care: Social responsibility, Public trust, Professional privilege, Community impact.

Professionalism and Society:
Dentistry involves: Service to others, Moral responsibility, Specialized knowledge, Professional autonomy.

Why Society Grants Privileges:
Society allows dentists: Self-regulation, Respect and professional status, Patient trust, Financial independence.
In return: Ethical conduct, Competence, Public protection (Protect patient welfare).

Dentist's Roles in Society:
Dentists contribute through: A. Public health promotion, B. Health education, C. Environmental awareness, D. Legal/forensic roles, E. Protecting patients from harm.

Dual Loyalty:
Dentist Loyalty to: 1. Individual Patient, 2. Society.

Examples of Dual Loyalty Conflicts:
Dentists may need to report: A. Infectious diseases, B. Child abuse, C. Human rights violations.

Industry and Commercial Conflicts:
Dentists must critically evaluate: Dental products, Pharmaceutical claims, Manufacturer marketing.

Resource Allocation:
Healthcare Resources (limited): Time, Equipment, Money, Workforce.

Levels of Resource Allocations:
Macro level — National decisions
Meso level — Hospital/clinic decisions
Micro level — Dentist decisions

Ethical Allocation Approaches:
Libertarian – Pay-based access
Utilitarian – Greatest benefit
Egalitarian – Equal need
Restorative – Help disadvantaged

Dentist Decisions at Micro Level:
Dentists decide: Radiographs frequency, Treatment complexity, Referral necessity.

Public Health Responsibilities:
Public health is about improving community health. Dentists should: Educate patients, Promote prevention, Identify social health risks.

Dentist as Public Health Advocate: Health education programs, Reporting hazards, Supporting prevention policies.

Global Health: Cross-border diseases, Shared health challenges, International cooperation (e.g., COVID-19, SARS).

Globalization and Dentistry: Migration of dentists, Refugee oral health needs, Workforce imbalance.

Ethical Responsibility in Global Workforce (FDI recommendations):
A. Prevent exploitation
B. Support fair recruitment
C. Maintain workforce balance

Case: A dentist must report a contagious disease but patient asks for secrecy.

Summary:
1. Dentistry operates under a social contract.
2. Dual loyalty creates ethical challenges.
3. Resource allocation requires fairness.
4. Dentists contribute to public and global health.
""",

    "1_5": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 5
Dentist and Colleagues / Employee Relationship Rights

Learning outcomes: Describe the ethical responsibilities of dentists toward colleagues and dental staff. Identify unethical behaviors in professional relationships (e.g., fee-splitting, patient attraction). Explain how teamwork and conflict resolution contribute to safe and ethical patient care.

Dentistry is not practiced alone. Dentists work with:
A. Other dentists
B. Specialists
C. Dental assistants
D. Hygienists
E. Laboratory technicians
F. Physicians and pharmacists

Dental Ethics Beyond the Patient:
Dental ethics includes duties toward: Patients, Colleagues, Society.
Ethical behavior must be consistent in all professional relationships.

Core Ethical Principles Applied to Professional Relationships:
Autonomy – Respect professional judgment
Beneficence – Work together for patient benefit
Non-maleficence – Avoid harming patients through ego or competition
Justice – Fair treatment of colleagues
Veracity – Honesty in communication

Respect Among Dentists:
Dentists must: Treat colleagues with dignity, Avoid public criticism, Communicate professionally, Focus on patient welfare.
Professional disagreement is acceptable. Professional disrespect is not.

Referral Ethics:
Refer when: 1. The case exceeds their competence, 2. Specialized skills are required, 3. Patient safety is at risk.
Referral must be based on patient benefit, not financial advantage.

Unethical Referral Practices:
1. Fee-splitting – Receiving money for referring patients; Violates justice and beneficence.
2. Attracting patients from colleagues – Undermining another dentist; Using negative comments to gain patients.

Managing Previous Faulty Treatment:
If you see poor work from another dentist: 1. Avoid harsh criticism, 2. Do not speculate, 3. Focus on current patient care, 4. Explain objectively.
Professional integrity requires discretion.

Dentist and Employee Relationship:
The dentist is: A. The leader of the dental team, B. Legally responsible for patient care, C. Responsible for supervision.
The staff must work within their scope.

Scope of Practice of Dental Assistants:
Dental assistants can NOT: diagnose, establish fees, judge treatment quality. Must follow the dentist's supervision.

Teamwork in Dentistry:
Effective dental teams require: A. Communication, B. Defined responsibilities, C. Mutual respect, D. Shared goal: best patient care.
Poor teamwork increases the risk of errors.

Leadership Responsibility:
A. Maintain a safe environment
B. Ensure equipment readiness
C. Supervise infection control
D. Take ultimate responsibility

Self-Regulation of Dentistry:
Dentistry is a self-regulating profession. Society grants: Trust, Privileges, Autonomy. In return, the profession must maintain high ethical standards.

Reporting Unsafe or Unethical Behavior:
Recognize unsafe practices, Avoid silent complicity, Follow institutional reporting procedures.
Protecting patients is more important than protecting colleagues.

Conflict Resolution:
A. Understand communication styles
B. Focus on the issue, not the person
C. Address problems early
D. Be patient and professional

The Code of Ethics and Ethical Principles:
No fee-splitting — Justice & Beneficence
No false advertising — Veracity
Refer when beyond competence — Non-maleficence
Maintain confidentiality — Autonomy & Respect

ADA Code Principles:
Autonomy – Respect choices – Obtain informed consent
Non-maleficence – Do no harm – Refer beyond competence
Beneficence – Promote welfare – Provide emergency care
Justice – Be fair – No fee-splitting
Veracity – Be honest – No false advertising

Summary:
A. Respect colleagues
B. Refer appropriately
C. Avoid financial conflicts
D. Supervise staff responsibly
E. Promote teamwork
F. Maintain professional integrity
""",

    "1_6": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 6
Confidentiality and Patients Records

Learning outcomes: Explain the ethical importance of patient confidentiality in dental practice. Describe the types of information included in dental records and how they must be protected. Identify situations where confidentiality may ethically or legally be breached.

What Are Dental Records?
Dental records contain: A. Patient's personal information, B. Medical history, C. Diagnostic data, D. Clinical notes, E. Radiographs and photos, F. Dentist–patient communication, G. Consent documentation.
These records help ensure continuity and quality of care.

Why Are Dental Records Important?
Dental records help: 1. Diagnose conditions, 2. Plan treatment, 3. Monitor patient progress, 4. Communicate with other healthcare professionals, 5. Protect dentist legally.

Ethical Duty of Confidentiality:
All dental professionals must: Protect patient information, Use information only for healthcare purposes, Prevent unauthorized access.
Breaching confidentiality can lead to legal consequences.

Patient Rights: A. Privacy, B. Control over their personal information, C. Access their health records, D. Expect professional confidentiality.

Health Records and Data Protection:
Health records contain information about: 1. Physical health, 2. Mental health, 3. Medical conditions.
These records must be protected by data protection laws.

Data Collectors:
A data controller is the person responsible for managing patient information.
Responsibilities: 1. Protecting patient data, 2. Determining how data is used, 3. Ensuring confidentiality.

Access to Patient Information:
Patient information should only be accessed by: A. Dentist, B. Dental assistants, C. Staff directly involved in treatment.

Confidentiality After Death: Confidentiality continues even after the patient dies. Ethical duty remains to protect patient information.

Securing Patient Information:
Locked filing cabinets, Password-protected computer systems, Restricted access to electronic records, Confidential conversations.

Confidentiality in Clinic Design:
Reception and treatment areas must: 1. Prevent conversations from being overheard, 2. Protect patient privacy, 3. Secure patient files.

Social Media and Confidentiality:
Dentists must never post patient information online without permission. Even anonymized cases must be carefully protected.

Patient Photos: Before using patient photos: A. Obtain written consent, B. Explain how images will be used, C. Ensure patient identity protection.

Ethical Basis of Confidentiality: Autonomy, Respect for persons, Trust. Without confidentiality, patients may hide important information.

When Confidentiality May Be Breached:
Confidentiality can be breached in exceptional situations: 1. Legal requirements, 2. Protection of others from harm, 3. Mandatory reporting (child abuse).

Dual Loyalty:
Dual loyalty occurs when dentists have responsibilities toward: A. Patient, B. Society, C. Government, D. Employers.

Example: If a patient refuses to inform their partner about HIV risk, disclosure may sometimes be justified to protect others.

Summary:
A. Confidentiality is essential in healthcare
B. Dental records must be secure
C. Patient trust depends on privacy
D. Breaches are allowed only in exceptional situations
""",

    "1_7": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 7
Legal Regulation in Dentistry (National and International)

Learning outcomes: Explain why dentistry is regulated by law. Identify the legal responsibilities of dentists in clinical practice. Compare national and international systems that regulate dentistry.

Why Is Dentistry Regulated?
A. Protect patient safety
B. Ensure qualified professionals provide treatment
C. Maintain professional standards
D. Prevent malpractice and negligence

What Do Legal Regulations Define?
A. Who is allowed to practice dentistry
B. Required qualifications and licensing
C. Standards of care
D. Professional responsibilities
E. Penalties for misconduct or malpractice

Importance of Legal Regulation:
A. Protect patients' rights
B. Maintain public trust in dentistry
C. Ensure ethical practice
D. Provide accountability for professional misconduct

Standards of Care:
National Standard of Care – Dentists are judged according to national professional standards.
Locality Rule – Dentists are evaluated according to standards in their local community.

Authorities That Regulate Dentistry:
1. Ministry of Health
2. Dental Councils
3. National Dental Associations

Legal Responsibilities of Dentists:
A. Obtain informed consent
B. Maintain accurate patient records
C. Follow infection control standards
D. Avoid negligence or malpractice
E. Protect patient confidentiality
Failure to follow these duties can lead to legal action.

Common Legal Issues in Dentistry:
Misdiagnosis or treatment error, Lack of informed consent, Breach of confidentiality, Failure to refer complex cases, False advertising or unlicensed practice.

International Regulation of Dentistry:
WHO – promotes global oral health policies
FDI World Dental Federation – develops ethical guidelines
International dental organizations – encourage professional standards

National vs International Regulation:
National: Government or dental council authority, country-specific scope, controls dental practice.
International: Global organizations, worldwide standards, promotes global quality.

Cultural Practices and Dental Ethics:
Some cultures historically practiced: Grinding front teeth for aesthetics, Removing certain teeth for cultural identity. These practices illustrate how cultural traditions may conflict with modern dental ethics.

Acceptable Tooth Extraction:
Extraction of healthy teeth may be justified only in: A. Orthodontic treatment, B. Correcting severe malocclusion. Such treatment must follow professional standards of care.

Regulation of Dentistry in Kurdistan Region:
A. Dentistry is regulated by the Kurdistan Dental Association (KDA)
B. The Dentists Syndicate Law (2004) governs practice
C. Dentists must be members of the KDA to practice legally

Regulation in Iraq: Iraq Dental Association oversees licensing and professional regulation.

Regulation in the United States: American Dental Association (ADA), Commission on Dental Accreditation (CODA), Regional dental licensing boards.

Regulation in Canada: National Dental Examining Board of Canada (NDEB), Commission on Dental Accreditation of Canada, Royal College of Dentists of Canada.

Key Points: Dentistry is regulated by law to protect patients. Dentists must follow legal and ethical standards. National and international organizations guide dental practice.
""",

    "1_8": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 8
Business Ethics in Dentistry

Learning outcomes: Explain how business pressures influence ethical decision-making in dentistry. Identify unethical practices in advertising, treatment planning, and financial decisions. Apply ethical principles to conflicts between patient care and business interests.

Dentistry as a Profession and a Business:
Patients pay for treatment. Dentists earn income. Ethical duties must still be followed.

Professional vs Business Ethics:
Professional Ethics: Patient-centered, Focus on care, Ethical duty.
Business Ethics: Profit-driven, Focus on revenue, Financial sustainability.
Problems arise when business decisions override professional ethics.

Importance of Legal Regulation:
A conflict of interest (COI) occurs when personal or financial interests influence clinical decisions.
COI is not always unethical, but it creates risk. Having a conflict is normal — but acting unfairly because of it is unethical.

Personal vs Patient Interest:
A. Choosing faster but poorer treatment
B. Scheduling based on convenience instead of quality
C. Selecting profit over best care

Public vs Patient Interest:
Dentists sometimes must balance: Individual patient needs and Limited resources (time, cost, public systems).

Third-Party Influence:
Third parties may influence decisions: A. Insurance companies, B. Employers, C. Government systems.
The dentist must always recommend the best treatment for the patient, even if financial systems limit it.

Ethical Advertising:
Advertising should: Be truthful, Be evidence-based, Provide information, not manipulation.

Unethical Advertising:
A. False claims
B. Digitally enhanced results
C. Claiming superiority over other dentists

Inducements and Discounts:
A. Gifts for patients
B. Referral rewards
C. Heavy discounts
Problems: Influences patient decisions unfairly.

Social Media in Dentistry:
Avoid: Misleading before and after images, Creating unrealistic expectations, Promoting unnecessary treatments.

Competitive Spirit vs Integrity:
Competition may lead to: 1. Overtreatment, 2. Undermining colleagues, 3. Financial bias.

Aesthetic and Cosmetic Dentistry:
Esthetic Dentistry: Restores function and natural appearance.
Cosmetic Dentistry: Changes appearance beyond normal.

Ethical Issues in Cosmetic Dentistry:
A. Treating healthy teeth unnecessarily
B. Following trends instead of science
C. Patient pressure vs professional judgment

Extending Scope of Practice:
Dentists must: Work within competence, Avoid performing unfamiliar procedures, Refer when needed.

New / Unproven Treatments:
Dentists must: Use evidence-based treatments, Avoid promoting unproven techniques (e.g., unnecessary frenectomy in infants).

Unscientific Treatments:
Unethical examples: Rejecting proven treatments (fluoride, endodontics), Promoting fake or unsupported methods.

Non-Dental Treatments:
Such as: Botox (outside proper indication), Fillers, tattoos, piercing. These may fall outside dentistry and can be unethical depending on context.

Unacceptable Business Practices:
Overtreatment, Undertreatment, Charging for services not done, Overcharging or undercharging, Cutting corners.

Summary:
Dentistry is both business and profession. Ethics must guide financial decisions. Avoid conflicts of interest. Use evidence-based practice. Protect patient trust.
""",

    "1_9": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 9
Informed Consent

Learning outcomes: Explain the concept and components of informed consent. Identify different types of consent and decision-making situations. Understand how justice influences access to dental care and resource distribution.

An Informed Consent:
A process of communication between dentist and patient that allows the patient to make a decision.
It is: a legal requirement, an ethical duty, part of patient autonomy.

Why is it important?
A. It respects patient autonomy
B. It builds trust
C. It protects dentist legally
D. It improves decision-making

What Should be Explained?
A. Diagnosis
B. Treatment options (including no treatment)
C. Risks and benefits
D. Costs
E. Alternatives

The Components of a Valid Consent:
A. Information – sufficient explanation should be provided
B. Capacity – the patient can decide on their treatment
C. Voluntary – no pressure should be applied on the patient

Types of Consent:
A. Verbal consent
B. Written consent
C. Implied consent
D. Explicit consent
E. Presumed consent

Verbal and Written Consent:
Verbal: simple, low-risk procedures.
Written: surgical or high-risk procedures.

Implied vs Explicit Consent:
Implied: patient behavior (sitting in a chair).
Explicit: direct agreement for a treatment.

Presumed Consent (Emergencies): Patient is unconscious, immediate treatment is needed.

Consent in Children & Incompetent Patients:
Decisions made by parents. Replacement (someone else) may decide for adults. Emergency leads to presumed consent.

Substitute Decision Making:
A. Substituted judgment – what the patient would want
B. Best interest – what is best for the patient

Social Justice in Dentistry: Fair distribution of healthcare, Equal respect for all patients, Access to care.

Basic Needs and the Distribution of Care for Patients:
Consider: A. Urgency, B. Need, C. Fairness.

Contribution and Effort:
Some systems consider patient's role in their healthcare and hygiene practices. The main ethical concern: May be unfair or discriminatory to judge their habits.

Free Market View:
Healthcare based on ability to pay. Problem: Inequality in access. Healthcare being used as a business may conflict with justice.

Basic Dental Care Concept:
Everyone should be able to have: A. Emergency care, B. Pain relief, C. Basic treatment. This is the minimum ethical standard.

Ethical thinking: Dentists must balance Individual patient needs, Limited resources, Fairness.

Summary:
Informed consent is communication and understanding. Valid consent requires 3 elements. Different types of consent exist. Justice ensures fairness in care.
""",

    "1_10": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 10
Ethical Considerations in Pediatric Dentistry

Learning outcomes: Understand ethical challenges in treating children. Explain informed consent in pediatric dentistry. Balance autonomy, beneficence, and parental influence. Analyze ethical dilemmas in pediatric cases.

Why do we consider Pediatric Dentistry to be different?
A. Children are still developing
B. Limited ability to decide
C. They depend on their parents
D. There are emotional and psychological factors

If treatment is essential, parents and dentists prioritize the child's benefit. A child's autonomy is different from an adult's, so communication is important. The dentist should explain treatment in a simple, age-appropriate way to involve the child and make them feel safe.

Triangle in Pediatric Dentistry:
Three entities are involved: 1. Dentist, 2. Parent, 3. Child.
Decisions are not made by one person; they involve all three.

Ethical Principles: Autonomy, Beneficence, Non-maleficence, Justice.

Communication with Children:
A. You must use simple language
B. You must consider age and development
C. You must make the child feel safe

Informed Consent in Children:
The parents will give legal consent for the child. The child should still be involved.

Child Assent:
The child should agree to the treatment, even if not legally required.

Balancing Autonomy and Beneficence:
Problem: Child refuses treatment but treatment is needed. This creates a conflict between respecting autonomy and doing what is best for the child.

Integrity (Dignity): Respecting the child as a person, Not ignoring the child's feelings, Not focusing only on the parents.

Autonomy in Children:
A. Not fully developed autonomy
B. Their autonomy grows with age
C. Their autonomy must be respected gradually

Role of the Parents:
Parents should: Give consent, Act in the child's best interest.
BUT: They may have conflicts due to (fear, time, stress).

Dentist as Child Advocate:
A dentist must: A. Protect the child's best interest, B. Question harmful decisions, C. Balance parent and child needs.
A dentist's duty is to the child first.

When Principles Conflict:
Child refuses treatment but treatment is beneficial. Conflict: Autonomy vs Beneficence.

When to Postpone Treatment:
A. If it's not urgent
B. If the child is very anxious
C. If better cooperation will be achieved later

When Immediate Treatment is Needed:
A. Trauma (avulsion) happens
B. Infection is present
In emergencies, beneficence may override autonomy.

Pain Control & Behavior Management:
The dentist must try to: A. Reduce pain, B. Use behavior techniques, C. Consider sedation if needed. Reduction of suffering is an ethical treatment.

Child Neglect and Abuse: The dentist must have the skills to recognize signs and report appropriately.

Ethical Analysis:
Consider: Child, Parent, Dentist, Society.
Evaluate using: Autonomy, Beneficence, Justice.

Summary:
Pediatric ethics is complex. Child plus parent plus dentist interaction. Balancing autonomy and beneficence. Always act in child's best interest.
""",

    "1_11": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 11
Negligence and Litigation in Dentistry

Learning outcomes: Define negligence clearly. Identify its key elements. Recognize legal risks in dental practice. Understand how to prevent litigation.

When ethical practice fails, legal consequences follow. Complaints may lead to legal cases. Early communication can prevent litigation.

Negligence:
Negligence: Failure to provide the standard of care expected from a dentist, resulting in harm to the patient.
Not every mistake is negligence. Harm must be present.

Examples of Negligence:
A. Not diagnosing caries
B. Wrong extraction
C. Ignoring infection
All of these points will lead to patient harm.

Elements of Negligence:
1. Duty of care
2. Breach of duty
3. Causation
4. Damage

Duty of Care:
Dentist–patient relationship exists. Dentist must provide proper care.

Breach of Duty:
The care provided falls below the standard of care.
Examples: Wrong diagnosis, Poor technique, No consent.

Standard of Care:
Based on average skilled dentist. Higher skill expected for complex procedures.
If you do implants, you are judged as an implant dentist — not a beginner.

Causation: Your action must cause the harm.

Damage (Injury): Physical, Psychological, Financial. If there is no injury, there is no case.

Non-Negligent Situations:
A. Known complications
B. Proper consent taken
C. Patient non-compliance
A bad outcome does not mean the dentist is wrong.

Liability of Dentist:
The responsibility of a dentist covers: A. Their work, B. Staff actions.

Breach of Contract:
A. In private treatment, a patient can complain to the dentist if the result does not meet the agreed standard.
B. The patient does not need to prove negligence, only that the treatment was not satisfactory.
C. Treatment should be safe, functional, and of good quality.
D. If it is not, the patient can reject the treatment and claim compensation.

Compensation:
Financial payment only (the only remedy for injury in civil claims is money).
Types: A. General (pain), B. Special (costs).
Examples: Pain and suffering, Treatment costs, Future care.

Legal Process:
1. Complaint
2. Investigation
3. Expert review
4. Court
Patients usually use a specialized lawyer. Dentists are supported by a defense organization.

Prevention:
Good communication, Proper consent, Documentation, Follow standards.
Most lawsuits are prevented by communication, not skill.

Summary:
Negligence is a combination of breach and harm. It requires 4 elements. Not all outcomes are negligence. Prevention is key.
""",

    "1_12": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 12
Substituted Consent for Dental Care Decisions

Learning outcomes: Define substituted consent and when it is used. Identify patients with compromised decision-making capacity. Understand the role of parents and legal guardians. Apply ethical reasoning to clinical cases.

Substituted Consent:
Consent given by another person on the patient's behalf.
Used when the patient: A. Can't understand, B. Can't decide, C. Can't communicate.

Capacity to Decide:
Capacity is the ability to: 1. Understand information, 2. Evaluate options, 3. Make a decision, 4. Communicate choice.

Who doesn't have the Capacity to decide?
A. Children
B. Unconscious patients
C. Patients with mental disability
D. Severe illness or confusion

Substituted Decision Makers: Parents, Legal guardians, Court-appointed decision makers.

Types of Substituted Consent:
1. Implied Consent – Shown by the patient's actions (sitting in a chair, opening the mouth); only for examination.
2. Verbal Consent – Spoken agreement; used for simple, low-risk procedures (scaling, simple filling).
3. Written Consent – Signed document; required for surgical/high-risk procedures (extraction, implants).
4. Explicit Consent – Clear, informed agreement (verbal or written); required for treatment plans.
5. Presumed Consent – Used in emergencies when the patient is unable to respond.

Role of Parents & Guardians:
Act in the child's best interest, Make informed decisions, Consider long-term outcomes.

The Responsibility of The Dentist:
Protect patient welfare. Do not blindly follow parents' decisions. Act as patient advocate.

Substituted Judgment:
What would the patient choose? Used when patient previously expressed wishes. Respects the patient's values even if they can't speak.

Best Interest Standard:
What is the best medical treatment for the patient? Used when patient preferences are unknown.

The capacity of a Patient:
A. Full capacity
B. Partial capacity
C. No capacity
Most patients are in the middle, where ethics becomes difficult.

Partial Capacity:
Elderly patient with mild dementia, Anxious or confused patient, A child who understands partially.
These patients should still be involved in decisions.

Managing Partial Capacity Patients:
A. Simplifying information for them
B. Check their understanding
C. Involve the patient and guardians
D. Respect the patient as much as possible

Ethical Conflicts:
A. Patient refuses treatment
B. Guardian agrees
C. Dentist sees benefit

Decision-Making in Ethical Conflicts:
Consider: 1. Patient's wishes, 2. Medical benefit, 3. Risk of harm, 4. Urgency.
Ethics should be balanced; decisions shouldn't be made blindly.

When to Override Refusal:
A. Serious harm is expected
B. Patient lacks capacity
C. Treatment is urgent

Assignment: An elderly patient with confusion refuses treatment, but family members agree that treatment should be done.
1. Does the patient have full decision-making capacity?
2. Who should make the final decision?
3. Which ethical principles are involved?
4. What is the most appropriate action for the dentist?

Summary:
Capacity determines consent. Substituted consent is common. Parents/guardians play key role. Patient must still be involved. Dentist protects patient interest.
""",

    "1_13": """EDM 101 – Ethics and Patients' Rights in Dental Medicine – Lecture 13
Medical & Dental Research Ethics

Learning outcomes: Understand why research is important in dentistry. Identify ethical requirements in research. Explain risks, benefits, and consent in research. Recognize unethical research behavior.

Why do we have ethics in research?
1. In the past, research was done without consent
2. Patients were harmed

Historical Examples: Experiments done without permission; Harm and death occurred.

Nuremberg Code (1949):
A set of ethical research principles for human experimentation created by the court to define the limits of permissible medical experimentation on human beings.
1. Voluntary informed consent is essential.
2. Human research has to be based on prior animal experiments.
3. Justification of benefit to individuals and society.
4. No expectation of physical and mental suffering and injury.
5. No expectation of death/injury from an experiment.
6. The risk should not exceed the benefits from the experiment's results.
7. Proper preparations for the experiments to protect the experimental subject.
8. Scientifically qualified persons should experiment.
9. Human subjects must have the freedom to end the experiment if they feel physically or mentally unable to continue.
10. Scientists must be ready to stop the experiment at any point if continuing could cause injury, disability, or death.

Belmont Report:
Defines 3 main principles: A. Respect for persons, B. Beneficence, C. Justice.
Contains Ethical Principles and Guidelines for the Protection of Human Subjects of Research.

Declaration of Helsinki:
The World Medical Association (WMA) developed this as a statement of ethical principles for medical research involving human participants, including research using identifiable human material or data.

Importance of Research: Improves treatments, Develops new materials, Enhances patient care.

Research in Dental Practices: Evidence-based dentistry, Better decision-making, Improved outcomes.

Ethical Requirements:
Research must include: A. Ethical approval, B. Scientific validity, C. Social value.

Ethics Committee Approval: Research must be approved before starting.

Scientific Merit: 1. Research must be well-designed, 2. Based on evidence.

Social Value: Research should benefit society.

Risk and Benefits: Risks must be minimized. Benefits must be greater.

Informed Consent in Research:
A. The purpose of the study (Purpose)
B. The risks involved (Risk)
C. The benefits (if any) (Benefit)
D. Their right to withdraw at any time (Right to withdraw)

Confidentiality: Patient data must be protected. No unauthorized sharing.

Conflict of Roles: Dentist and researcher. Main issue: Patient trust against research goals.

Honest Reporting: Report results honestly. Do not hide negative results.

Whistle Blowing: Reporting unethical research.

Issues Faced: A. Funding problems, B. Technology limitations, C. Diverse populations.

Assignment: A dentist conducts research on patients but does not fully explain risks.
A. Is this ethical?
B. What is missing, and what ethical principles were violated?
C. What is the ideal way for the researcher/dentist to act?
""",
}

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

client = genai.Client(api_key=GEMINI_KEY)


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

    if data.startswith("sem_"):
        sem_id = data[len("sem_"):]
        context.user_data["sem"] = sem_id
        topics = LECTURES[sem_id]["topics"]

        if not topics:
            await query.edit_message_text(f"📂 {LECTURES[sem_id]['name']}\n\n⚠️ No lectures added yet.")
            return

        keyboard = []
        for t_id, t_name in topics.items():
            key = f"{sem_id}_{t_id}"
            status = "✅" if key in lecture_contents else "📤"
            keyboard.append([InlineKeyboardButton(f"{status} {t_name}", callback_data=f"topic_{key}")])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
        await query.edit_message_text(
            f"📂 {LECTURES[sem_id]['name']} - Choose:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("topic_"):
        key = data[len("topic_"):]
        sem_id, topic_id = key.split("_", 1)
        topic_name = LECTURES[sem_id]["topics"][topic_id]
        context.user_data['current_lecture'] = key

        if key in lecture_contents:
            keyboard = [
                [InlineKeyboardButton("❓ Ask Question", callback_data=f"ask_{key}")],
                [InlineKeyboardButton("📝 Generate Quiz", callback_data=f"quiz_{key}")],
                [InlineKeyboardButton("🔄 Re-Upload PDF", callback_data=f"upload_{key}")],
                [InlineKeyboardButton("🔙 Back", callback_data=f"sem_{sem_id}")]
            ]
            await query.edit_message_text(
                f"✅ *{topic_name}* is ready!\n\nWhat would you like to do?",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            context.user_data['awaiting_upload'] = key
            await query.edit_message_text(
                f"📤 *{topic_name}* has no content yet.\n\nPlease **send the PDF file** for this lecture right here in this chat.",
                parse_mode="Markdown"
            )

    elif data.startswith("upload_"):
        key = data[len("upload_"):]
        context.user_data['awaiting_upload'] = key
        await query.edit_message_text("📤 Please send the new PDF file for this lecture.")

    elif data.startswith("ask_") or data.startswith("quiz_"):
        if data.startswith("ask_"):
            key = data[len("ask_"):]
            action = "ask"
            prompt_hint = "✍️ Type your question below."
        else:
            key = data[len("quiz_"):]
            action = "quiz"
            prompt_hint = "✍️ Type 'yes' to generate a 5-question quiz, or type your specific topic."
        context.user_data['current_lecture'] = key
        context.user_data['action'] = action
        await query.edit_message_text(prompt_hint)

    elif data == "back":
        await start(update, context)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get('awaiting_upload')
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
        context.user_data['awaiting_upload'] = None

        sem_id, topic_id = key.split("_", 1)
        topic_name = LECTURES[sem_id]["topics"][topic_id]
        await update.message.reply_text(
            f"✅ *{topic_name}* uploaded successfully! ({len(text)} characters)\n\n"
            f"Click /start, go to Semester {sem_id}, and select it to ask questions!",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error reading PDF: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    key = context.user_data.get('current_lecture')
    action = context.user_data.get('action', 'ask')

    if not key or key not in lecture_contents:
        await update.message.reply_text("⚠️ Please select a lecture first using the /start menu.")
        return

    lecture_text = lecture_contents[key]
    sem_id, topic_id = key.split("_", 1)
    topic_name = LECTURES[sem_id]["topics"][topic_id]

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

        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        await update.message.reply_text(
            f"🧑‍🏫 *{topic_name}*\n\n{response.text}",
            parse_mode="Markdown"
        )
        context.user_data['action'] = 'ask'
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
