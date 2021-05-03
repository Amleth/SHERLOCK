<!-- http://www.cidoc-crm.org/crminf/sites/default/files/CRMinf%20ver%2010.1.pdf -->
<!-- https://docs.google.com/presentation/d/1kLy--Qf3mCoLMYxE264ihiIXUgXSLkWzqFTad8weVcI/edit#slide=id.g1dbd9620c4_0_22 -->

**E7 Activity**
    SUBCLASSES:
        **I1 Argumentation**
            EXAMPLES::
                "My classification and dating of this bowl (I5)"
                "My adoption of the belief that Dragendorfftype 29 bowls are from the 1stCentury AD (I7)"
            PROPERTIES:
                *J2 concluded that (was concluded by) --> I8 Conviction*
                    EXAMPLES::
                        "My classification and dating of this bowl (I5) concluded thatmy belief that this bowl is from the 1st Century AD (I2)"
                    SUBPROPERTY OF:
                        *P116 starts (is started by)*
            SUBCLASSES:
                **S4 Observation**
                **I5 Inference Making/S5 Inference Making**
                    EXAMPLES::
                        "My classification and dating of this bowl"
                    SUBCLASSES:
                        **S6 Data Evaluation**
                        **S7 Simulation or Prediction**
                        **S8 Categorical Hypothesis Building**
                    PROPERTIES:
                        *J1 used a premise (was premise for) --> I8 Conviction*
                            EXAMPLES::
                                "My classification and dating of this bowl (I5) used as premise my belief that Dragendorff type 29 bowls are from the 1st Century AD (I2)"
                                "My classification and dating of this bowl (I5) used as premise my belief in the observations of this bowl (I2)"
                            SUBPROPERTY OF:
                                *P17 was motivated by (motivated) [E7 --> E1]*
                        *J3 applies (was applied by) --> I3 Inference Logic*
                            EXAMPLES::
                                "My classification and dating of this bowl (I5) applies Use of a typology (I3)"
                            SUBPROPERTY OF:
                                *P16 used specific object (was used for) [E7 --> E70]*
                **I7 Belief Adoption**
                    EXAMPLES::
                        "My adoption of the belief that Dragendorff type 29 bowls are from the 1st Century AD"
                    PROPERTIES:
                        *J6 adopted (adopted by) --> I2 Belief*
                            EXAMPLES::
                                "My adoption of the belief that Dragendorff type 29 bowls are from the 1st Century AD (I7) adopted Dragendorff’s belief that type 29 bowls are from the 1st Century AD (I2)"
                            SUBPROPERTY OF:
                                *P17 was motivated by (motivated) [E7 --> E1]*
                        *J7 is based on evidence (is evidence for) --> E73 Information Object*
                            EXAMPLES::
                                "My adoption of the belief that Dragendorff type 29 bowls are from the 1st Century AD (I7) is based on evidence from Hans Dragendorff, "Terra sigillata. Ein Beitrag zur Geschichte der griechischen und römischen Keramik", Bonner Jahrbücher96 (1895), 18-155 (E73)"
                            SUBPROPERTY OF:
                                *P16 used specific object (was used for) [E7 --> E70]*
                        *J11 used manifestation (was manifestation used by) --> F3 Manifestation*
                            SCOPE:
                                This property is a shortcut over the long path: I7 Belief adoption:J6 adopted:I2 Belief:J4 that (is subject of):I4 Proposition Set: P148 has component(is component of):E89 Propositional Object:P148i has component (is component of):F1 Work: R3 is realised in (realises):F2 Expression:R4i is embodied in:F3 Manifestation
                            EXAMPLES:
                                "My adoption of the belief that Dragendorff type 29 bowls are from the 1st Century AD (I7) J11used manifestation(was manifestation used by)"Terra sigillata. Ein Beitrag zur Geschichte der griechischen und römischen Keramik", BonnerJahrbücher96 (1895), 18-155 (F3)"
                                "Martin’s citation that Nero was singing in Rome while it was burning J11 used manifestation (was manifestation used by)manifestation of De Vita Caesarum by Gaius Suetonius Tranquillus"
                        *J12 used (was used by) --> F5 Item*
                            SCOPE:
                                This property is a shortcut over the long path: I7 Belief Adoption:J6 adopted:I2 Belief: J2i was concluded by: I5/S5 Inference Making: J1 used as premise (was premise for): E25 Human-Made Feature:O16 observed value (value was observed by): S4 Observation: O8 observed (was observed by): F5 Item
                            EXAMPLES:
                                "My adoption of the belief that Dragendorff type 29 bowls are from the 1st Century AD (I8) J12 used (was used by) The Institute of Archaeologies’ copy of "Terra sigillata. Ein Beitrag zur Geschichte der griechischen und römischen Keramik", Bonner Jahrbücher96 (1895), 18-155 (F5)"
                                "Martin’s citation that Nero was singing in Rome while it was burning J12 used (was used by) Martin’s copy of  De Vita Caesarum by Gaius Suetonius Tranquillus"
**E2 Temporal Entity**
    SUBCLASSES:
        **I8 Conviction**
            EXAMPLES::
                "My belief that Gaius Suetonius Tranquillus was deliberately lying about Nero."
            SUBCLASSES:
                **I2 Belief**
                    EXAMPLES::
                        "My belief that Dragendorff type 29 bowls are from the 1st Century AD"
                        "Dragendorff’s belief that type 29 bowls are from the 1st Century AD"
                    PROPERTIES:
                        *J4 that (is subject of) --> I4 Proposition Set*
                            EXAMPLES::
                                "Dragendorff’s belief that type 29 bowls are from the 1st Century AD (I2) that Type 29 bowls are from the 1st Century AD (I4)"
                        *J5 holds to be --> I6 Belief Value*
                            EXAMPLES::
                                "Dragendorff’s belief that type 29 bowls are from the 1st Century AD (I2) holds to be True (I6)"
                **I9 Provenanced Comprehension**
                    EXAMPLES::
                        "My citation and belief that the extant book De Vita Caesarum attributed to Gaius Suetonius Tranquillus stated 121AD that Nero was singing in Rome while it was burning from July 19 in 1464 AD."
                    PROPERTIES:
                        *J8 understands (is understood by) --> E73 Information Object*
                            EXAMPLES:
                                "My citation that Nero was singing in Rome while it was burning understands the extant book De Vita Caesarum by Gaius Suetonius Tranquillus"
                        *J9 believes in porovenance (provenance is believed by) --> I10 Provenance Statement*
                            EXAMPLES:
                                "My citation that Nero was singing in Rome while it was burning believes in provenancethat the content of the extant book De Vita Caesarum by Gaius Suetonius Tranquillus was published in Rome 121AD"
                        *J10 reads as -> I4 Information Set*
                            EXAMPLES:
                                "My citation that Nero was singing in Rome while it was burning reads as “Nero, while watching Rome burn, exclaimed how beautiful it was, and sang an epic poem about the sack of Troy while playing the lyre”"
**E89 Propositionnal Object**
    SUBCLASSES:
        **I3 Inference Logic**
            EXAMPLES::
                "Dating using a reference typology"
                "User of parallels"
**E73 Information Object**
    **I4 Proposition Set**
        EXAMPLES::
            "The Dragendorff Samian typology"
            "Type 29 bowls are from the 1st Century AD(need to formulate as a set of CRM statements)"
        SUBCLASSES:
            **I10 Provenance Statement**
                EXAMPLES:
                    "The Latin content of the extant book De Vita Caesarum attributed to Gaius Suetonius Tranquillus was published in Rome 121AD and not alienated in its propositional content by essential transcription errors until its currently knownform."
                    "The exemplar of The Merchant of Venice, Quarto 1 (1600) owned by The British Library, shelf number BL C.34.k.22 was published 1600AD by Thomas Heyes."
**E59 Primitive Value**
    SUBCLASSES:
        **I6 Belief Value**