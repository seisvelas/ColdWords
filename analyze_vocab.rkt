#lang racket

(require db)
(require db/util/postgresql)
(require plot)

; load credentials from .py
(define credentials (string-split (file->string "database_credentials.py") "\""))

; hackishly parse
(define USER (second credentials))
(define PASSWORD (fourth credentials))
(define SERVER (sixth credentials))
(define DATABASE "postgres")

(define WORD-ARRAYS-QUERY
  (file->string "word_arrays.sql"))

(define SMALLEST-IDEOLOGY-QUERY
  (file->string "smallest_ideology.sql"))

(define pgc
  (postgresql-connect #:user USER
                      #:database DATABASE
                      #:password PASSWORD
                      #:server SERVER))

; type token ratio punishes long texts,
; we compensate by getting an equal quantity
; of words for each ideology
(define WORDS-LIMIT
  (query-value pgc SMALLEST-IDEOLOGY-QUERY))

(define (analyze-wordset wordset)
  (let ((ideology (vector-ref wordset 0))
        (words (take (pg-array->list (vector-ref wordset 1))
                     WORDS-LIMIT)))
    (list ideology
          (exact->inexact
           ; TTR formula: length(set(text)) / length(text)
           (/ (length (remove-duplicates words))
              (length words))))))

(define (ideologies->histogram ideologies)
  (plot-file
 (discrete-histogram
  (map (lambda (x)
         (vector (first x)
                 (ivl .26 (second x))))
       ideologies)
  #:color "darkred"
  #:line-color "black"
  #:y-min .275
  #:y-max .283)
 #:title "Ideologies"
 #:x-label ""
 #:y-label "Type Token Ratio"
 "histogram.png"))

; returns big lists of all words found for each ideology 
(let ((ideologies-words (query-rows pgc WORD-ARRAYS-QUERY)))
  (ideologies->histogram (map analyze-wordset
                              ideologies-words)))