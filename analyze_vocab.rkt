#lang racket

(require db)
(require db/util/postgresql)

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
        (words (take (pg-array->list (vector-ref wordset 1)) WORDS-LIMIT)))
    (list ideology
          (exact->inexact
           (/ (length (remove-duplicates words))
              (length words))))))

; returns big lists of all words found for each ideology 
(let* ((ideologies-words (query-rows pgc WORD-ARRAYS-QUERY)))
  (display (map analyze-wordset
                ideologies-words)))

