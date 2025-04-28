UPDATE "${table_name}"
SET status = reverse (
	SUBSTRING ( reverse ( LPAD( status, ${bit_number}, 'n' ) ) :: TEXT FROM 1 FOR ${up_index} ) || ${status_number} || SUBSTRING ( reverse ( LPAD( status, ${bit_number}, 'n' ) ) :: TEXT FROM ${next_index} )
),
status_meta = jsonb_set (
		"${table_name}".status_meta,
		'{state_time,${current_index}}',
		jsonb_set (
			COALESCE ( "${table_name}".status_meta #> '{state_time,${current_index}}', jsonb_build_object ( '${status_number}', '${current_time}' ) ),
			'{${status_number}}',
			CONCAT ( '"', '${current_time}', '"' ) :: JSONB
		)
	)