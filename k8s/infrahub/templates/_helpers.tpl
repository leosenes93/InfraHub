{{- define "infrahub.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "infrahub.fullname" -}}
{{- .Release.Name -}}
{{- end -}}

{{- define "infrahub.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" -}}
{{- end -}}

{{- define "infrahub.labels" -}}
app.kubernetes.io/name: {{ include "infrahub.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ include "infrahub.chart" . }}
{{- end -}}

{{- define "infrahub.selectorLabels" -}}
app.kubernetes.io/name: {{ include "infrahub.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "infrahub.databaseUrl" -}}
{{- printf "postgresql+psycopg://%s:%s@%s-postgres:5432/%s" .Values.postgres.user .Values.postgres.password (include "infrahub.fullname" .) .Values.postgres.database -}}
{{- end -}}
