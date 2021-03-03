import React, { useState } from 'react';

export default function Home() {
	const [file, setFile] = useState(null);

	const handleNewFile = (e: React.ChangeEvent<HTMLInputElement>) => {};

	return (
		<div>
			<input type='file' onChange={(e) => e.target.files} />
		</div>
	);
}
