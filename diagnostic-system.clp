; ========================================
; Expert System: Diagnosis of Telematics Terminal-device 
; Purpose: Determine device malfunction by LED color, power status and internal state
; ========================================

(deftemplate device
    "Template: Terminal-device status"

    (slot power 
        (type SYMBOL)
        (allowed-symbols on off unknown)
        (default unknown))
    (slot led-color 
        (type SYMBOL)
        (allowed-symbols red green yellow blank unknown)
        (default unknown))
    (slot internal-state 
        (type SYMBOL)
        (allowed-symbols ok errfile erraddress errunkn unknown)
        (default unknown))
)

(deffunction start ()
    "Function: Power on the system, create device fact"

    (reset)
    (assert (device))
    (run)
)

(deffunction ask-slot-value-with-validation (?template-based-fact ?slot)
    "Function: Ask question to fill out one slot of the template"

    (bind ?allowed-inputs (deftemplate-slot-allowed-values ?template-based-fact ?slot))
    (if (eq ?allowed-inputs FALSE)
    then
        (printout t "Get allowed inputs: Fail / Slot " ?slot " allowed-values is empty" crlf)
        (halt)
    )

    (while TRUE
        (printout t "What's the status of " ?slot " - " ?allowed-inputs crlf)
        (bind ?user-input (lowcase (read)))
        (if (member$ ?user-input ?allowed-inputs)
        then
            (return ?user-input)
        else 
            (printout t "Validate answer: Fail / Allowed answers are: " ?allowed-inputs crlf)
        )
    )
)

(defrule check-device-power
    ?device-id <- (device (power unknown))
    =>
    (bind ?user-input (ask-slot-value-with-validation device power))
    (modify ?device-id (power ?user-input))
)
