<script setup lang="ts">
import type { components } from '@/api/schema'
import { PrimeIcons } from '@primevue/core/api'
import { downloadFile } from '@/util'

export type FileTableProps = {
  requiredFileTypes: components['schemas']['FileBase']['file_type'][]
}

type FileCrudProps = {
  caseId?: string
  trackId?: string
  appointmentId?: string
} & FileTableProps

const props = defineProps<FileCrudProps>()

const { token, baseUrl } = useApiClient()
const caseId = toRef(props, 'caseId')
const trackId = toRef(props, 'trackId')
const appointmentId = toRef(props, 'appointmentId')
const {
  files,
  fetchMany: fetchFiles,
  updateFile,
  deleteFile,
} = useFile(caseId, trackId, appointmentId)
fetchFiles()

function getDownloadUrl(fileId: string) {
  if (props.caseId) {
    return `${baseUrl}/api/file/${fileId}?case_id=${props.caseId}`
  } else if (props.trackId) {
    return `${baseUrl}/api/file/${fileId}?track_id=${props.trackId}`
  } else if (props.appointmentId) {
    return `${baseUrl}/api/file/${fileId}?appointment_id=${props.appointmentId}`
  } else {
    throw new Error('Either caseId or trackId must be provided')
  }
}

type FileBase = components['schemas']['FileBase']

const fileTableConfig: TableColumnConfig<FileBase>[] = [
  {
    key: 'filename',
    label: () => 'Bestandsnaam',
    dataType: 'custom',
  },
  {
    key: 'file_type',
    label: () => 'Bestandstype',
    dataType: 'text',
  },
  {
    key: 'approved',
    label: () => 'Goedgekeurd',
    dataType: 'boolean',
  },
  {
    key: 'description',
    label: () => 'Omschrijving',
    dataType: 'custom',
  },
  {
    key: 'created_at',
    label: () => 'Geupload op',
    dataType: 'datetime',
  },
]

const { me } = useAuth()
function getMenuItems(file: FileBase) {
  const menuItems: ContextMenuItem<'Verwijderen' | 'Goedkeuren' | 'Goedkeuring intrekken'>[] = [
    {
      icon: PrimeIcons.CHECK_SQUARE,
      label: 'Goedkeuren',
      hide:
        !file.approval_required || file.approved || !me.value?.permissions.includes('file:approve'),
    },
    {
      icon: PrimeIcons.TIMES_CIRCLE,
      label: 'Goedkeuring intrekken',
      hide: !file.approved || !me.value?.permissions.includes('file:approve'),
    },
    {
      icon: PrimeIcons.TRASH,
      label: 'Verwijderen',
      hide: file.approved || !me.value?.permissions.includes(getRequiredPermission('delete')),
    },
  ]
  return menuItems
}
const missingFiles = computed(() => {
  const existingFileTypes = files.value?.map((f) => f.file_type)
  return props.requiredFileTypes.filter(
    (fileType) => existingFileTypes && !existingFileTypes.includes(fileType),
  )
})

const { askToConfirm } = useConfirm()

async function handleApprove(file: FileBase, approved: boolean) {
  await askToConfirm({
    question: approved
      ? `Weet je zeker dat je het bestand ${file.filename} wilt goedkeuren?`
      : `Weet je zeker dat je de goedkeuring van het bestand ${file.filename} wilt intrekken?`,
    title: 'Bestand goedkeuren',
  })
  await updateFile(
    {
      approved,
      file_type: file.file_type,
      description: file.description,
    },
    file.id,
  )
}

async function handleDelete(file: FileBase) {
  await askToConfirm({
    question: `Weet je zeker dat je het bestand ${file.filename} wilt verwijderen?`,
    title: 'Bestand verwijderen',
  })
  await deleteFile(file.id)
}

type ArrayElement<T> = T extends (infer ElementType)[] ? ElementType : never
type Permissions = ArrayElement<components['schemas']['User']['permissions']>

function getRequiredPermission(action: 'create' | 'read' | 'update' | 'delete') {
  let permission
  if (props.caseId) {
    permission = `case:file:${action}` as Permissions
  } else if (props.trackId) {
    permission = `track:file:${action}`
  } else if (props.appointmentId) {
    permission = `appointment:file:${action}`
  } else {
    throw new Error('Either caseId, trackId or appointmentId must be provided')
  }
  return permission as Permissions
}

async function handleDownload(fileId: string, token: string) {
  await downloadFile(getDownloadUrl(fileId), token)
}
</script>

<template>
  <template v-if="missingFiles.length > 0">
    <h3 class="my-4">Benodigde bestanden die nog niet zijn geüpload</h3>
    <table>
      <thead>
        <tr>
          <th>Bestandstype</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="fileType in missingFiles" :key="fileType">
          <td>{{ fileType }}</td>
          <td>
            <FileUploadCustom
              :appointment-id="appointmentId"
              :case-id="caseId"
              :track-id="trackId"
              :file-type="'Plan van aanpak'"
              @upload-completed="fetchFiles()"
            />
          </td>
        </tr>
      </tbody>
    </table>

    <h3 class="my-4">Geüploade bestanden</h3>
  </template>

  <FileUploadCustom
    :appointment-id="appointmentId"
    :case-id="caseId"
    :track-id="trackId"
    :file-type="'Overig'"
    @upload-completed="fetchFiles()"
    v-if="me?.permissions.includes(getRequiredPermission('create'))"
  />

  <OcTable
    v-if="files"
    :data="files"
    :table-config="fileTableConfig"
    :id-key="'id'"
    :limit="5"
    show-action-column
  >
    <template #custom="{ row: currentFile, column }">
      <template v-if="column.key == 'filename'">
        <Button
          v-if="token"
          :icon="PrimeIcons['DOWNLOAD']"
          class="mr-2"
          size="small"
          :variant="'text'"
          :label="currentFile.filename"
          @click="handleDownload(currentFile.id, token)"
          :disabled="!me?.permissions.includes(getRequiredPermission('read'))"
        />
      </template>
      <template v-if="column.key == 'description'">
        <InputText
          :model-value="currentFile.description"
          :placeholder="`Omschrijving van ${currentFile.filename}`"
          :disabled="currentFile.approved"
          @update:model-value="
            (value) =>
              updateFile(
                {
                  description: value || null,
                  approved: currentFile.approved,
                  file_type: currentFile.file_type,
                },
                currentFile.id,
              )
          "
        />
      </template>
    </template>
    <template #action="{ row: currentFile }">
      <ContextMenu
        :menu-items="getMenuItems(currentFile)"
        @item-clicked="
          async (item) => {
            if (item.label === 'Verwijderen') {
              await handleDelete(currentFile)
            } else if (item.label == 'Goedkeuren') {
              await handleApprove(currentFile, true)
            } else if (item.label == 'Goedkeuring intrekken') {
              await handleApprove(currentFile, false)
            }
            fetchFiles()
          }
        "
      />
    </template>
  </OcTable>
</template>
