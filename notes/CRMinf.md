# Tree

**E13 Attribute Assignment**
    Subclasses:
        **I1 Argumentation**
            Examples:
                "My classification and dating of this bowl (I5)"
                "My adoption of the belief that Dragendorfftype 29 bowls are from the 1stCentury AD(I7)"
            Properties:
                *J2 concluded that (was concluded by) --> I2 Belief*
                    Examples:
                        "My classification and dating of this bowl (I5) concluded thatmy belief that this bowl is from the 1st Century AD (I2)"
                    Subproperty of:
                        *P116 starts (is started by)*
            Subclasses:
                **S4 Observation**
                **I5 Inference Making/S5 Inference Making**
                    Examples:
                        "My classification and dating of this bowl"
                    Subclasses:
                        **S6 Data Evaluation**
                        **S7 Simulation or Prediction**
                        **S8 Categorical Hypothesis Building**
                    Properties:
                        *J1 used a premise (was premise for) --> I2 Belief*
                            Examples:
                                "My classification and dating of this bowl (I5) used as premise my belief that Dragendorff type 29 bowls are from the 1st Century AD (I2)"
                                "My classification and dating of this bowl (I5) used as premise my belief in the observations of this bowl (I2)"
                            Subproperty of:
                                *P17 was motivated by (motivated) [E7 --> E1]*
                        *J3 applies (was applied by) --> I3 Inference Logic*
                            Examples:
                                "My classification and dating of this bowl (I5) applies Use of a typology(I3)"
                            Subproperty of:
                                *P16 used specific object (was used for) [E7 --> E70]*
                **I7 Belief Adoption**
                    Examples:
                        "My adoption of the belief that Dragendorff type 29 bowls are from the 1st Century AD"
                    Properties:
                        *J6 adopted (adopted by) --> I2 Belief*
                            Examples:
                                "My adoption of the belief that Dragendorff type 29 bowls are from the 1st Century AD (I7) adopted Dragendorff’s belief that type 29 bowls are from the 1st Century AD (I2)"
                            Subproperty of:
                                *P17 was motivated by (motivated) [E7 --> E1]*
                        *J7 is based on evidence (is evidence for) --> E73 Information Objec*
                            Examples:
                                "My adoption of the belief that Dragendorff type 29 bowls are from the 1st Century AD (I7) is based on evidencefromHans Dragendorff, "Terra sigillata. Ein Beitrag zur Geschichte der griechischen und römischen Keramik", BonnerJahrbücher96 (1895), 18-155(E73)"
                            Subproperty of:
                                *P16 used specific object (was used for) [E7 --> E70]*
**E2 Temporal Entity**
    Subclasses:
        **I2 Belief**
            Examples:
                "My belief that Dragendorff type 29 bowls are from the 1st Century AD"
                "Dragendorff’s belief that type 29 bowls are from the 1st Century AD"
            Properties:
                *J4 that (is subject of) --> I4 Proposition Set*
                    Examples:
                        "Dragendorff’s belief that type 29 bowls are from the 1st Century AD (I2) that Type 29 bowls are from the 1st Century AD (I4)"
                *J5 holds to be --> I6 Belief Value*
                    Examples:
                        "Dragendorff’s belief that type 29 bowls are from the 1st Century AD (I2) holds to be True (I6)"
**E89 Propositionnal Object**
    Subclasses:
        **I3 Inference Logic**
            Examples:
                "Use of a typology"
                "User of parallels"
**E73 Information Object**
    **I4 Proposition Set**
        Examples:
            "The Dragendorff Samian typology"
            "Type 29 bowls are from the 1st Century AD(need to formulate as a set of CRM statements)"
**E59 Primitive Value**
    Subclasses:
        **I6 Belief Value**