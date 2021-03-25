/*******************************************************************************
 * Copyright 2021 Mike Pawlowski
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 *******************************************************************************/
"use strict";

// ESLint Rule Overrides

/* globals emit */

// Views ---------------------------------------------------------------------->

var conflictsView = function (doc) {
	if (doc._conflicts) {
		var name = null;

		if (doc.entity &&
				doc.entity.name) {
			name = doc.entity.name;
		}

		emit(name, doc._conflicts);
	}
};

module.exports = {
	language: "javascript",
	type: "design_document",
	version: 1,
	views: {
		conflicts: {
			map: conflictsView
		}
	}
};